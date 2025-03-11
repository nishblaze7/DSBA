import os
import streamlit as st
import pandas as pd
import asyncio
from transformers import AutoModelForQuestionAnswering, AutoTokenizer
import torch

# Fix potential asyncio event loop issues
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

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
st.markdown("- *What was the revenue for Customer X?* \n- *Who is the sales rep for Customer Y?* \n- *What was the revenue for a customer in Q1 2024?*")

# Ensure correct file path for Book4.xlsx
file_path = os.path.join(os.path.dirname(__file__), "Book4.xlsx")

# Load dataset with error handling
@st.cache_resource()
def load_data():
    try:
        df = pd.read_excel(file_path, engine="openpyxl")  # Ensure openpyxl is used
        # Standardizing column names for easier matching
        df.columns = df.columns.str.lower().str.replace(" ", "_")
        return df
    except FileNotFoundError:
        st.error("⚠️ File 'Book4.xlsx' not found! Ensure it's uploaded in the repo.")
        return None

df = load_data()

# Column Mapping for Different Types of Queries
COLUMN_MAPPINGS = {
    "revenue": ["dummy_gross_rev", "dummy_net_rev"],
    "sales_rep": ["sales_person_id"],
    "time": ["month", "quarter", "date"],
    "customer": ["dummy_customer_name"]
}

# Input box for user query
user_query = st.text_input("Enter your query:", "What was the revenue for customer Venqb in Jan-23?")

# Step 1: Identify Relevant Columns Based on Query
def identify_relevant_columns(query):
    query = query.lower()
    
    if any(word in query for word in ["revenue", "gross", "net", "total sales"]):
        return COLUMN_MAPPINGS["revenue"]
    
    elif any(word in query for word in ["sales person", "rep", "account owner"]):
        return COLUMN_MAPPINGS["sales_rep"]
    
    elif any(word in query for word in ["month", "quarter", "date", "year"]):
        return COLUMN_MAPPINGS["time"]
    
    elif any(word in query for word in ["customer", "company", "client"]):
        return COLUMN_MAPPINGS["customer"]
    
    return []  # Default to an empty list if no clear match

# Step 2: Find Matching Rows Based on Query
def find_relevant_context(query, dataframe):
    if dataframe is None:
        return "Dataset not available."
    
    relevant_columns = identify_relevant_columns(query)
    if not relevant_columns:
        return "No relevant columns identified for this query."
    
    # Search only in relevant columns
    query_lower = query.lower()
    match = dataframe[relevant_columns].apply(lambda row: any(query_lower in str(value).lower() for value in row), axis=1)
    filtered_df = dataframe[match]
    
    if not filtered_df.empty:
        return filtered_df.to_dict(orient="records")  # Return structured data
    else:
        return "No relevant data found."

# Step 3: Extract the Answer from Matched Data
def generate_answer(question, matched_data):
    if isinstance(matched_data, str):
        return matched_data  # Return "No relevant data found."

    # Format results into a readable response
    results = []
    for row in matched_data:
        for key, value in row.items():
            results.append(f"**{key.replace('_', ' ').title()}**: {value}")

    return "\n".join(results)

# Step 4: Process User Query
if st.button("Search"):
    with st.spinner("🔍 Searching..."):
        matched_data = find_relevant_context(user_query, df)
        result = generate_answer(user_query, matched_data)
    
    # Display Results
    st.subheader("📌 Answer:")
    st.write(result)
