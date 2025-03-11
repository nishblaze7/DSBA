import os
import streamlit as st
import pandas as pd
from transformers import AutoModelForQuestionAnswering, AutoTokenizer
import torch

# Load model from Hugging Face
MODEL_NAME = "Nishchandan/streamlit-bert-model"  # Update with your model repo

@st.cache_resource()
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForQuestionAnswering.from_pretrained(MODEL_NAME)
    return tokenizer, model

tokenizer, model = load_model()

st.title("💡 Financial Semantic Search")
st.markdown("### Ask a financial question like:")
st.markdown("- *What was the revenue for Customer X?* \n- *Who is the account owner for Customer Y?*")

# **Ensure correct file path for Book4.xlsx**
file_path = os.path.join(os.path.dirname(__file__), "Book4.xlsx")

# Load dataset with error handling
@st.cache_resource()
def load_data():
    try:
        df = pd.read_excel(file_path, engine="openpyxl")  # Ensure openpyxl is used
        
        # **Clean column names** - Remove leading/trailing spaces & convert to lowercase
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        return df
    except FileNotFoundError:
        st.error("⚠️ File 'Book4.xlsx' not found! Ensure it's uploaded in the repo.")
        return None

df = load_data()

# Input box for user query
user_query = st.text_input("Enter your query:", "What was the revenue for customer Aaapm in Q1 2024?")

# **Step 1: Search the most relevant row in the dataset**
def find_relevant_context(query, dataframe):
    if dataframe is None:
        return "Dataset not available."
    
    query_lower = query.strip().lower()  # Normalize query
    best_match = None
    max_matches = 0
    
    for _, row in dataframe.iterrows():
        match_count = sum(query_lower in str(value).strip().lower() for value in row)
        if match_count > max_matches:
            max_matches = match_count
            best_match = row.astype(str).to_dict()  # Convert row to dictionary
    
    if best_match:
        return " ".join([f"{k}: {v}" for k, v in best_match.items()])  # Create structured context
    else:
        return "No relevant data found."

# **Step 2: Use BERT to Answer the Question**
def get_answer(question, context):
    if context == "No relevant data found.":
        return context
    
    inputs = tokenizer(question, context, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Extract the most probable answer
    answer_start = torch.argmax(outputs.start_logits)
    answer_end = torch.argmax(outputs.end_logits) + 1
    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][answer_start:answer_end]))

    # Handle cases where answer extraction fails
    if not answer.strip():
        return "No clear answer found. Try rephrasing your question."
    
    return answer

if st.button("Search"):
    with st.spinner("🔍 Searching..."):
        # Step 1: Extract relevant data from the dataset
        extracted_context = find_relevant_context(user_query, df)
        
        # Step 2: Run BERT model only if relevant data is found
        result = get_answer(user_query, extracted_context)
    
    # **Display Results**
    st.subheader("📌 Answer:")
    st.write(f"**{result}**")
