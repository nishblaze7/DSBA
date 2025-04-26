# Streamlit App: Customer Revenue NLP Query Engine

import streamlit as st
import pandas as pd
import difflib
import datetime

# Load Data
def load_data():
    df = pd.read_excel('NPL Sample.xlsx')
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()
customer_list = df['Customer Name'].unique()

# Month Map
month_map = {
    'jan': 1, 'january': 1,
    'feb': 2, 'february': 2,
    'mar': 3, 'march': 3,
    'apr': 4, 'april': 4,
    'may': 5,
    'jun': 6, 'june': 6,
    'jul': 7, 'july': 7,
    'aug': 8, 'august': 8,
    'sep': 9, 'september': 9,
    'oct': 10, 'october': 10,
    'nov': 11, 'november': 11,
    'dec': 12, 'december': 12
}

# Correct minor typos in month names
def correct_month_typo(word):
    matches = difflib.get_close_matches(word.lower(), month_map.keys(), n=1, cutoff=0.7)
    if matches:
        return month_map[matches[0]]
    return None

# NLP Engine
def smarter_nlp_query(question, data):
    question = question.lower()
    words = question.split()

    customer_name = None
    for word in words:
        match = difflib.get_close_matches(word, [cust.lower() for cust in customer_list], n=1, cutoff=0.7)
        if match:
            for real_name in customer_list:
                if real_name.lower() == match[0]:
                    customer_name = real_name
                    break
            if customer_name:
                break

    month_found = None
    for month_key in month_map.keys():
        if month_key in question:
            month_found = month_map[month_key]
            break

    if not month_found:
        for word in words:
            month_found = correct_month_typo(word)
            if month_found:
                break

    import re
    year_found = None
    current_year = datetime.datetime.now().year

    year_match = re.search(r'20\d{2}', question)
    if year_match:
        year_found = int(year_match.group(0))
    elif "last year" in question:
        year_found = current_year - 1
    elif "this year" in question:
        year_found = current_year
    elif "last" in question and month_found:
        year_found = current_year - 1
    elif "this" in question and month_found:
        year_found = current_year

    if not customer_name:
        return "Sorry, could not recognize the customer name. Please check spelling."
    if not month_found:
        return "Sorry, could not recognize the month. Please specify the month."
    if not year_found:
        return "Sorry, could not recognize the year. Please specify the year or say 'last year' or 'this year'."

    result = data[(data['Customer Name'] == customer_name) &
                  (data['Date'].dt.year == year_found) &
                  (data['Date'].dt.month == month_found)]

    if not result.empty:
        revenue = result['Net Revenue'].sum()
        month_name = result.iloc[0]['Month']
        if revenue == 0:
            answer = f"{customer_name} had no recorded revenue in {month_name} {year_found}."
        else:
            answer = f"{customer_name} made ${revenue:,.2f} in {month_name} {year_found}."
        return answer
    else:
        return "No matching record found."

# Streamlit App UI
st.set_page_config(page_title="Customer Revenue NLP", layout="wide", page_icon="🚚")

# Custom Correct CSS for Carolina Blue Theme with pop-out box
st.markdown("""
    <style>
    .stApp {
        background-color: #e6f2ff;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton>button {
        background-color: #4B9CD3;
        color: white;
        font-size: 18px;
        border-radius: 10px;
        padding: 0.5rem 2rem;
    }
    .stTextInput>div>div>input {
        background-color: #ffffff;
        border: 2px solid #4B9CD3;
        border-radius: 12px;
        padding: 15px;
        font-size: 18px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Page Content
st.title("🚚 Customer Revenue NLP Query Engine")

st.markdown("""
### Empowering Logistics Insights
Example Question: **How much revenue did ABLKM make last March?**
""")

user_question = st.text_input("Enter your question:")

if st.button("Submit Query"):
    if user_question:
        response = smarter_nlp_query(user_question, df)
        st.success(response)
    else:
        st.warning("Please enter a question!")

st.markdown("---")
st.caption("Built for Corporate Logistics - Powered by NLP ✨")
