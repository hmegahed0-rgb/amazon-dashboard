import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import hashlib

# ================= CONFIG =================
st.set_page_config(page_title="Elite SaaS Dashboard", layout="wide", page_icon="📊")

# ================= DB =================
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT,
    password TEXT
)
""")
conn.commit()

# ================= AUTH FUNCTIONS =================
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

# ================= LOGIN UI =================
if not st.session_state.auth:

    st.title("🔐 SaaS Login System")

    choice = st.radio("Choose Action", ["Login", "Signup"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if choice == "Signup":
        if st.button("Create Account"):
            signup(username, password)
            st.success("Account Created! Now login.")

    if choice == "Login":
        if st.button("Login"):
            if login(username, password):
                st.session_state.auth = True
                st.success("Login successful 🚀")
                st.rerun()
            else:
                st.error("Invalid credentials")

    st.stop()

# ================= HEADER =================
st.markdown("""
# 📊 Elite Amazon SaaS Dashboard
### 🤖 AI • 📈 Analytics • 💰 Business Intelligence
---
""")

# ================= UPLOAD =================
file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])

if file is None:
    st.info("Upload file to start analytics 🚀")
    st.stop()

# ================= LOAD DATA =================
df = pd.read_excel(file)

# safe columns check
required = ['order_date', 'customer_region', 'product_category', 'total_revenue']
missing = [c for c in required if c not in df.columns]

if missing:
    st.error(f"Missing columns: {missing}")
    st.stop()

df['order_date'] = pd.to_datetime(df['order_date'])

# ================= SIDEBAR =================
st.sidebar.title("🎛 Control Panel")

page = st.sidebar.selectbox("Pages", ["Dashboard", "AI Analyst", "Export"])

region = st.sidebar.selectbox("Region", df['customer_region'].unique())
category = st.sidebar.multiselect("Category", df['product_category'].unique(),
                                  default=df['product_category'].unique())

filtered = df[
    (df['customer_region'] == region) &
    (df['product_category'].isin(category))
]

# ================= DASHBOARD =================
if page == "Dashboard":

    st.title("📊 Business Dashboard")

    # KPIs
    revenue = filtered['total_revenue'].sum()
    orders = len(filtered)
    avg_order = revenue / orders if orders > 0 else 0

    col1, col2, col3 = st.columns(3)

    col1.metric("💰 Revenue", f"{revenue:,.0f}")
    col2.metric("📦 Orders", orders)
    col3.metric("📊 AOV", f"{avg_order:,.0f}")

    # Charts
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

# ================= AI ANALYST =================
elif page == "AI Analyst":

    st.title("🧠 AI Business Analyst")

    revenue = filtered['total_revenue'].sum()
    orders = len(filtered)

    top_cat = filtered.groupby('product_category')['total_revenue'].sum().sort_values(ascending=False)

    insight = f"""
📌 **AI Generated Report**

💰 Total Revenue: {revenue:,.0f}  
📦 Total Orders: {orders}  
🏆 Top Category: {top_cat.index[0] if len(top_cat)>0 else 'N/A'}  

📊 **Insights:**
- Revenue distribution depends heavily on top categories  
- Region "{region}" shows distinct demand behavior  
- Scaling opportunity exists in mid-performing categories  

⚡ **Recommendation:**
- Increase marketing on top 2 categories  
- Optimize discount strategy  
- Expand in high-performing regions
"""

    st.success(insight)

# ================= EXPORT =================
elif page == "Export":

    st.title("📥 Export Data")

    csv = filtered.to_csv(index=False).encode('utf-8')

    st.download_button("Download Report", csv, "report.csv", "text/csv")
