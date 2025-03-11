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

# Load dataset (Book4.xlsx) - Ensure it's in the same directory as the app
@st.cache_resource()
def load_data():
    df = pd.read_excel("Book4.xlsx")  # Update filename if necessary
    return df

df = load_data()

# Input box for user query
user_query = st.text_input("Enter your query:", "What was the revenue for customer Aaapm in Q1 2024?")

# **Step 1: Search the most relevant row in the dataset**
def find_relevant_context(query, dataframe):
    query_lower = query.lower()
    match = dataframe.apply(lambda row: any(query_lower in str(value).lower() for value in row), axis=1)
    filtered_df = dataframe[match]
    
    if not filtered_df.empty:
        return " ".join(filtered_df.astype(str).values.flatten())  # Convert to text for BERT
    else:
        return "No relevant data found."

# **Step 2: Use BERT to Answer the Question**
def get_answer(question, context):
    inputs = tokenizer(question, context, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Extract the most probable answer
    answer_start = torch.argmax(outputs.start_logits)
    answer_end = torch.argmax(outputs.end_logits) + 1
    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][answer_start:answer_end]))
    
    return answer

if st.button("Search"):
    with st.spinner("🔍 Searching..."):
        # Step 1: Extract relevant data from the dataset
        extracted_context = find_relevant_context(user_query, df)
        
        # Step 2: Run BERT model only if relevant data is found
        if extracted_context != "No relevant data found.":
            result = get_answer(user_query, extracted_context)
        else:
            result = "No relevant information found in the dataset."
    
    # **Display Results**
    st.subheader("📌 Answer:")
    st.write(f"**{result}**")
