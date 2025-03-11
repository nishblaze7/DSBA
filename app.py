import streamlit as st
from transformers import AutoModelForQuestionAnswering, AutoTokenizer
import torch

# Load model from Hugging Face
MODEL_NAME = "Nishchandan/streamlit-bert-model"  # Update with your Hugging Face model repo

@st.cache_resource()
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForQuestionAnswering.from_pretrained(MODEL_NAME)
    return tokenizer, model

# Load the model and tokenizer
tokenizer, model = load_model()

st.title("💡 Financial Semantic Search")
st.markdown("### Ask a financial question like:")
st.markdown("- *What was the revenue for Customer X?* \n- *Who is the account owner for Customer Y?*")

# Input box for user query
user_query = st.text_input("Enter your query:", "What was the revenue for customer Aaapm in Q1 2024?")

# Sample context (Replace this with actual financial data context)
context = """
Customer Aaapm had a total revenue of $1,250,000 in Q1 2024. The revenue mainly came from logistics services and warehousing.
"""

def get_answer(question, context):
    inputs = tokenizer(question, context, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Extract the most probable answer
    answer_start = torch.argmax(outputs.start_logits)
    answer_end = torch.argmax(outputs.end_logits) + 1
    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][answer_start:answer_end]))
    
    return answer

if st.button("Search"):
    with st.spinner("🔍 Searching..."):
        result = get_answer(user_query, context)
    
    st.subheader("📌 Answer:")
    st.write(f"**{result}**")
