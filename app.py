import streamlit as st
from dtc_rag import qa_bot

def main():
    st.title("DTC Q&A System Using MistralAI")
    
    courses = [
    "data-engineering-zoomcamp",
    "machine-learning-zoomcamp",
    "mlops-zoomcamp"]
    zoomcamp_option = st.selectbox("Select a zoomcamp", courses)

    with st.form(key='rag_form'):
        prompt = st.text_input("Enter your prompt")
        response_placeholder = st.empty()
        submit_button = st.form_submit_button(label='Submit')
        
    

    if submit_button:
        response_placeholder.markdown("Loading...")
        response = qa_bot(prompt)
        response_placeholder.markdown(response)

if __name__ == "__main__":
    main()
    
#How to find deadlines for homeworks in mlops-zoomcamp ?