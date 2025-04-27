# Streamlit App: Customer Revenue NLP Query Engine (Clean Version)

import streamlit as st
import pandas as pd
import difflib
import datetime

# Page Setup
st.set_page_config(page_title="Customer Revenue NLP", layout="wide", page_icon="🚚")
st.title("🚚 Customer Revenue NLP Query Engine")

# Load Data
def load_data():
    try:
        df = pd.read_excel('NPL Sample.xlsx')
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except Exception as e:
        st.error(f"⚠️ Failed to load the data file: {e}")
        st.stop()

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

# Smarter NLP Query Engine
def smarter_nlp_query(question, data):
    responses = []
    subquestions = question.split("?")

    current_year = datetime.datetime.now().year

    for subq in subquestions:
        subq = subq.strip().lower()
        if not subq:
            continue
        words = subq.split()

        customer_name = None
        division_name = None
        account_owner_name = None

        # Match Customer, Division, Account Owner
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

        # Find Year
        import re
        year_found = None

        year_match = re.search(r'20\d{2}', subq)
        if year_match:
            year_found = int(year_match.group(0))
        elif "last year" in subq:
            year_found = current_year - 1
        elif "this year" in subq:
            year_found = current_year

        # Find Month
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

        # NEW: infer year if month is found but year missing and "last" or "this" is mentioned
        if month_found and year_found is None:
            if "last" in subq:
                year_found = current_year - 1
            elif "this" in subq:
                year_found = current_year

        # Handle Customer Start Date + Revenue Question
        if "how long" in subq and customer_name:
            cust_data = data[data['Customer Name'] == customer_name]
            if cust_data.empty:
                responses.append(f"No records found for {customer_name}.")
                continue

            first_date = cust_data['Date'].min()
            total_revenue = cust_data['Net Revenue'].sum()

            responses.append(
                f"{customer_name} has been a customer since {first_date.strftime('%B %Y')}. "
                f"Total revenue: ${total_revenue:,.2f}."
            )
            continue

        # Normal Customer Revenue lookup
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

        # Division Revenue lookup
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

        # Account Owner Lookup
        elif account_owner_name:
            accounts = data[data['Account Owner'] == account_owner_name]['Customer Name'].unique()
            account_list = ", ".join(accounts)
            if month_found and year_found:
                result = data[(data['Account Owner'] == account_owner_name) &
                              (data['Date'].dt.year == year_found) &
                              (data['Date'].dt.month == month_found)]
                total_revenue = result['Net Revenue'].sum()
                month_name = result['Month'].iloc[0] if not result.empty else ""
                responses.append(
                    f"{account_owner_name} owns {len(accounts)} accounts: {account_list}. "
                    f"In {month_name} {year_found}, total revenue was ${total_revenue:,.2f}."
                )
            else:
                full_result = data[data['Account Owner'] == account_owner_name]
                total_revenue = full_result['Net Revenue'].sum()
                responses.append(
                    f"{account_owner_name} owns {len(accounts)} accounts: {account_list}. "
                    f"Lifetime total revenue: ${total_revenue:,.2f}."
                )

        else:
            responses.append("Sorry, I couldn't understand part of the question.")

    return "\n\n".join(responses)

# Streamlit App Layout
st.markdown("""
### Empowering Logistics Insights
Examples:
- **How much revenue did "" make in March 2023?**
- **How much did Division "" make last May?**
- **How many accounts does"" own and what did they make in April 2024?**
- **How long has"" been a customer?**
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
