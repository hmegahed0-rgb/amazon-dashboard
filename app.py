import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import hashlib

# ================= CONFIG =================
st.set_page_config(page_title="Elite SaaS Dashboard", layout="wide", page_icon="📊")

# ================= DATABASE =================
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT,
    password TEXT
)
""")
conn.commit()

# ================= AUTH =================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def signup(username, password):
    c.execute("INSERT INTO users VALUES (?,?)", (username, hash_password(password)))
    conn.commit()

def login(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    return c.fetchone()

# ================= SESSION =================
if "auth" not in st.session_state:
    st.session_state.auth = False

# ================= LOGIN =================
if not st.session_state.auth:

    st.title("🔐 SaaS Login")

    choice = st.radio("Choose", ["Login", "Signup"])

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if choice == "Signup":
        if st.button("Create Account"):
            signup(user, pwd)
            st.success("Account created!")

    if choice == "Login":
        if st.button("Login"):
            if login(user, pwd):
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Wrong credentials")

    st.stop()

# ================= HEADER =================
st.markdown("""
# 📊 Amazon Elite Dashboard
### 🤖 AI • 📈 Analytics • 💰 BI System
---
""")

# ================= DATA SOURCE =================

st.sidebar.title("📂 Data Source")

uploaded_file = st.sidebar.file_uploader("Upload new dataset (optional)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
else:
    df = pd.read_excel("amazon_sales_dataset.xlsx")  # default dataset

# ================= VALIDATION =================
required = ['order_date', 'customer_region', 'product_category', 'total_revenue']
missing = [c for c in required if c not in df.columns]

if missing:
    st.error(f"Missing columns: {missing}")
    st.stop()

df['order_date'] = pd.to_datetime(df['order_date'])

# ================= FILTERS =================
st.sidebar.title("🎛 Filters")

region = st.sidebar.selectbox("Region", df['customer_region'].unique())

category = st.sidebar.multiselect(
    "Category",
    df['product_category'].unique(),
    default=df['product_category'].unique()
)

filtered = df[
    (df['customer_region'] == region) &
    (df['product_category'].isin(category))
]

# ================= PAGES =================
page = st.sidebar.selectbox("Pages", ["Dashboard", "AI Analyst", "Export"])

# ================= DASHBOARD =================
if page == "Dashboard":

    st.title("📊 Business Dashboard")

    revenue = filtered['total_revenue'].sum()
    orders = len(filtered)
    avg_order = revenue / orders if orders else 0

    col1, col2, col3 = st.columns(3)

    col1.metric("💰 Revenue", f"{revenue:,.0f}")
    col2.metric("📦 Orders", orders)
    col3.metric("📊 AOV", f"{avg_order:,.0f}")

    cat = filtered.groupby('product_category')['total_revenue'].sum().reset_index()

    fig1 = px.bar(cat, x='product_category', y='total_revenue', title="Revenue by Category")

    monthly = filtered.groupby(filtered['order_date'].dt.to_period("M"))['total_revenue'].sum().reset_index()
    monthly['order_date'] = monthly['order_date'].astype(str)

    fig2 = px.line(monthly, x='order_date', y='total_revenue', title="Monthly Trend")

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.plotly_chart(fig2, use_container_width=True)

# ================= AI =================
elif page == "AI Analyst":

    st.title("🧠 AI Analyst")

    revenue = filtered['total_revenue'].sum()
    orders = len(filtered)

    top_cat = filtered.groupby('product_category')['total_revenue'].sum().sort_values(ascending=False)

    st.success(f"""
📌 Revenue: {revenue:,.0f}  
📦 Orders: {orders}  
🏆 Top Category: {top_cat.index[0] if len(top_cat)>0 else 'N/A'}  

📊 Insights:
- Strong dependency on top categories  
- Region behavior varies  
- Growth opportunity exists  

🚀 Recommendation:
- Boost top products  
- Optimize discounts  
""")

# ================= EXPORT =================
elif page == "Export":

    st.title("📥 Export")

    csv = filtered.to_csv(index=False).encode('utf-8')

    st.download_button("Download CSV", csv, "report.csv", "text/csv")
