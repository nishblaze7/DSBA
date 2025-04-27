def load_data():
    try:
        df = pd.read_excel('NPL Sample.xlsx')
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except Exception as e:
        st.error(f"⚠️ Failed to load the data file: {e}")
        st.stop()

try:
    df = load_data()
    customer_list = df['Customer Name'].unique()
    division_list = df['Division'].unique()
    account_owner_list = df['Account Owner'].unique()
except Exception as e:
    st.error(f"⚠️ Failed during dataset parsing: {e}")
    st.stop()
st.title("🚚 Test Loading Revenue NLP Engine...")

st.success("✅ Data loading started...")

# (your loading code here)

st.success("✅ Data loaded and parsed successfully!")
