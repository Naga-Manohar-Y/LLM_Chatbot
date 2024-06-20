import os
from elasticsearch import Elasticsearch
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

# Initialize Elasticsearch

es = Elasticsearch("http://localhost:9200")

api_key = os.getenv('MISTRAL_API_KEY')

if not api_key:
    raise ValueError("API key not found. Please set the MISTRAL_API_KEY environment variable.")

# Initialize the client with the retrieved API key
client = MistralClient(api_key=api_key)


context_template = """
Section: {section}
Question: {question}
Answer: {text}
""".strip()

prompt_template = """
You're a course teaching assistant.
Answer the user QUESTION based on CONTEXT - the documents retrieved from our FAQ database.
Don't use other information outside of the provided CONTEXT.  

QUESTION: {user_question}

CONTEXT:

{context}
""".strip()



def retrieve_documents(query, index_name="course-questions", max_results=5):
    search_query = {
        "size": max_results,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["question^3", "text", "section"],
                        "type": "best_fields"
                    }
                },
                "filter": {
                    "term": {
                        "course": "data-engineering-zoomcamp"
                    }
                }
            }
        }
    }
    
    response = es.search(index=index_name, body=search_query)
    documents = [hit['_source'] for hit in response['hits']['hits']]
    return documents
        


def build_context(documents):
    context_result = ""
    
    for doc in documents:
        doc_str = context_template.format(**doc)
        context_result += ("\n\n" + doc_str)
    
    return context_result.strip()

def build_prompt(user_question, documents):
    context = build_context(documents)
    prompt = prompt_template.format(
        user_question=user_question,
        context=context
    )
    return prompt

def ask_mistral(prompt, model="open-mistral-7b"):
    response = client.chat(
        model=model,
        messages=[ChatMessage(role="user", content=prompt)]
    )
    answer = response.choices[0].message.content
    return answer

def qa_bot(user_question):
    context_docs = retrieve_documents(user_question)
    prompt = build_prompt(user_question, context_docs)
    answer = ask_mistral(prompt)
    return answer