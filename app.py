# Streamlit App: Customer Revenue NLP Query Engine (Expanded with Multi-Question Support)

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
division_list = df['Division'].unique()
account_owner_list = df['Account Owner'].unique()

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

# Smarter NLP Engine

def smarter_nlp_query(question, data):
    responses = []
    subquestions = question.split("?")

    for subq in subquestions:
        subq = subq.strip().lower()
        if not subq:
            continue
        words = subq.split()

        customer_name = None
        division_name = None
        account_owner_name = None

        for word in words:
            match = difflib.get_close_matches(word, [cust.lower() for cust in customer_list], n=1, cutoff=0.7)
            if match:
                for real_name in customer_list:
                    if real_name.lower() == match[0]:
                        customer_name = real_name
                        break
                if customer_name:
                    break

        for word in words:
            match = difflib.get_close_matches(word, [div.lower() for div in division_list], n=1, cutoff=0.7)
            if match:
                for real_name in division_list:
                    if real_name.lower() == match[0]:
                        division_name = real_name
                        break
                if division_name:
                    break

        for word in words:
            match = difflib.get_close_matches(word, [acct.lower() for acct in account_owner_list], n=1, cutoff=0.7)
            if match:
                for real_name in account_owner_list:
                    if real_name.lower() == match[0]:
                        account_owner_name = real_name
                        break
                if account_owner_name:
                    break

        import re
        year_found = None
        current_year = datetime.datetime.now().year

        year_match = re.search(r'20\d{2}', subq)
        if year_match:
            year_found = int(year_match.group(0))
        elif "last year" in subq:
            year_found = current_year - 1
        elif "this year" in subq:
            year_found = current_year

        month_found = None
        for month_key in month_map.keys():
            if month_key in subq:
                month_found = month_map[month_key]
                break

        if not month_found:
            for word in words:
                month_found = correct_month_typo(word)
                if month_found:
                    break

        if customer_name:
            if not month_found or not year_found:
                responses.append("Please specify the month and year when asking about a customer.")
            else:
                result = data[(data['Customer Name'] == customer_name) &
                              (data['Date'].dt.year == year_found) &
                              (data['Date'].dt.month == month_found)]
                if not result.empty:
                    revenue = result['Net Revenue'].sum()
                    month_name = result.iloc[0]['Month']
                    responses.append(f"{customer_name} made ${revenue:,.2f} in {month_name} {year_found}.")
                else:
                    responses.append("No matching customer revenue record found.")

        elif division_name:
            if not year_found:
                responses.append("Please specify the year when asking about a division.")
            else:
                result = data[(data['Division'] == division_name) &
                              (data['Date'].dt.year == year_found)]
                if not result.empty:
                    revenue = result['Net Revenue'].sum()
                    responses.append(f"Division {division_name} generated ${revenue:,.2f} in {year_found}.")
                else:
                    responses.append("No matching division revenue record found.")

        elif account_owner_name:
            accounts = data[data['Account Owner'] == account_owner_name]['Customer Name'].unique()
            account_list = ", ".join(accounts)
            if month_found and year_found:
                result = data[(data['Account Owner'] == account_owner_name) &
                              (data['Date'].dt.year == year_found) &
                              (data['Date'].dt.month == month_found)]
                total_revenue = result['Net Revenue'].sum()
                month_name = result['Month'].iloc[0] if not result.empty else ""
                responses.append(f"{account_owner_name} owns {len(accounts)} accounts: {account_list}. In {month_name} {year_found}, total revenue was ${total_revenue:,.2f}.")
            else:
                full_result = data[data['Account Owner'] == account_owner_name]
                total_revenue = full_result['Net Revenue'].sum()
                responses.append(f"{account_owner_name} owns {len(accounts)} accounts: {account_list}. Lifetime total revenue: ${total_revenue:,.2f}.")

        else:
            responses.append("Sorry, I couldn't understand part of the question.")

    return "\n\n".join(responses)

# Streamlit App UI
st.set_page_config(page_title="Customer Revenue NLP", layout="wide", page_icon="🚚")

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

st.title("🚚 Customer Revenue NLP Query Engine")

st.markdown("""
### Empowering Logistics Insights
Examples:
- **How much revenue did ABLKM make in March 2023?**
- **How much did Division X make in 2025?**
- **How many accounts does Account Owner Y own and what is their total revenue?**
- **How many accounts does Amy Walker own, and what did they make in March 2023?**
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
