import streamlit as st
from transformers import AutoModelForQuestionAnswering, AutoTokenizer

# Load model from Hugging Face
MODEL_NAME = "Nishchandan/streamlit-bert-model"  # Replace with your Hugging Face repo name

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

if st.button("Search"):
    st.write(f"🔍 Searching for: **{user_query}** (Results coming soon...)")
