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
        
        # Standardize column names (lowercase, replace spaces with underscores)
        df.columns = df.columns.str.lower().str.replace(" ", "_")
        
        # Rename any incorrect columns
        df.rename(columns={"dummry_gross_rev": "dummy_gross_rev"}, inplace=True)
        
        # Convert datetime columns to string for easier matching
        df['month'] = df['month'].astype(str)
        df['date'] = df['date'].astype(str)
        
        return df
    except FileNotFoundError:
        st.error("⚠️ File 'Book4.xlsx' not found! Ensure it's uploaded in the repo.")
        return None

df = load_data()

# Input box for user query
user_query = st.text_input("Enter your query:", "What was the revenue for customer Aaapm in Q1 2024?")

# **Step 1: Search for relevant data in specific columns**
def find_relevant_data(query, dataframe):
    if dataframe is None:
        return "Dataset not available."
    
    query_lower = query.lower()
    relevant_columns = ['dummy_customer_name', 'customer_id', 'month', 'quarter', 'dummy_gross_rev', 'dummy_net_rev', 'sales_person_id']
    
    match = dataframe[relevant_columns].apply(lambda row: any(query_lower in str(value).lower() for value in row), axis=1)
    filtered_df = dataframe[match]
    
    if not filtered_df.empty:
        return filtered_df.iloc[0].to_dict()  # Return the first matched row as a dictionary
    else:
        return "No relevant data found."

# **Step 2: Construct an Answer from Retrieved Data**
def generate_answer(query, data):
    if isinstance(data, str):  # If no relevant data was found
        return data
    
    if "revenue" in query.lower():
        return f"Customer {data['dummy_customer_name']} had a total revenue of ${data['dummy_gross_rev']} in {data['month']} ({data['quarter']})."
    
    if "sales person" in query.lower():
        return f"The sales person ID for {data['dummy_customer_name']} is {data['sales_person_id']}."
    
    return "I found some relevant data but couldn't generate a precise answer."

if st.button("Search"):
    with st.spinner("🔍 Searching..."):
        extracted_data = find_relevant_data(user_query, df)
        result = generate_answer(user_query, extracted_data)
    
    # **Display Results**
    st.subheader("📌 Answer:")
    st.write(f"**{result}**")
