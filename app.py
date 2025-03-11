import streamlit as st
import torch
from transformers import BertTokenizer, BertForQuestionAnswering
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load fine-tuned model and tokenizer
@st.cache_resource()
def load_model():
    model_path = "fine_tuned_bert"  # Update this with your actual path if needed
    tokenizer = BertTokenizer.from_pretrained(model_path)
    model = BertForQuestionAnswering.from_pretrained(model_path)
    return tokenizer, model

tokenizer, model = load_model()

# Load business/customer dataset
@st.cache_data()
def load_data():
    # Replace with actual dataset path
    df = pd.read_excel("Book4.xlsx", sheet_name="Data Source")
    return df

df = load_data()

# Function to encode text with BERT
@st.cache_data()
def encode_text(text):
    tokens = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model(**tokens)
    return outputs.start_logits.numpy().flatten()

# Generate embeddings for the dataset
@st.cache_data()
def generate_embeddings():
    df["embeddings"] = df["Dummy Customer Name"].apply(lambda x: encode_text(str(x)))
    return df

df = generate_embeddings()

# Function to search the best match

def search_query(query):
    query_embedding = encode_text(query)
    df["similarity"] = df["embeddings"].apply(lambda x: cosine_similarity([query_embedding], [x])[0][0])
    result = df.sort_values(by="similarity", ascending=False).head(3)  # Show top 3 matches
    return result[["Dummy Customer Name", "Dummry Gross Rev", "Sales Person ID", "similarity"]]

# Streamlit UI
st.title("💡 Financial Semantic Search")
st.markdown("### Ask a financial question like:")
st.markdown("- *What was the revenue for Customer X?* \n- *Who is the account owner for Customer Y?*")

user_query = st.text_input("Enter your query:", "What was the revenue for customer Aaapm in Q1 2024?")

if st.button("Search"):
    results = search_query(user_query)
    st.write("### 🔍 Top Matches:")
    st.dataframe(results)
