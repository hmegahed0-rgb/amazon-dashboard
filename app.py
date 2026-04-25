import streamlit as st
import pandas as pd
import plotly.express as px

# ================= CONFIG =================
st.set_page_config(
    page_title="Amazon BI Elite Dashboard",
    layout="wide",
    page_icon="📊"
)

st.markdown("""
# 📊 Amazon Business Intelligence Dashboard (ELITE)
### 🤖 AI Insights • 📈 Analytics • 📦 Sales Intelligence
---
""")

# ================= UPLOAD =================
file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])

if file:

    # ================= DATA =================
    df = pd.read_excel(file)
    df['order_date'] = pd.to_datetime(df['order_date'])

    # ================= SIDEBAR =================
    st.sidebar.title("🎛️ Control Panel")

    region = st.sidebar.selectbox("Region", df['customer_region'].unique())
    categories = st.sidebar.multiselect(
        "Categories",
        df['product_category'].unique(),
        default=df['product_category'].unique()
    )

    filtered_df = df[
        (df['customer_region'] == region) &
        (df['product_category'].isin(categories))
    ]

    # ================= KPIs =================
    st.markdown("## 📌 Executive KPIs")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Revenue", f"{filtered_df['total_revenue'].sum():,.0f}")
    col2.metric("📦 Orders", filtered_df.shape[0])
    col3.metric("⭐ Rating", round(filtered_df['rating'].mean(), 2))
    col4.metric("💸 Discount", f"{filtered_df['discount_percent'].mean():.1f}%")

    # ================= CHARTS =================
    st.markdown("## 📊 Analytics Overview")

    cat = filtered_df.groupby('product_category')['total_revenue'].sum().reset_index()

    fig1 = px.bar(cat, x='product_category', y='total_revenue',
                  color='total_revenue', color_continuous_scale='Blues',
                  title="Revenue by Category")

    monthly = filtered_df.groupby(filtered_df['order_date'].dt.to_period('M'))['total_revenue'].sum().reset_index()
    monthly['order_date'] = monthly['order_date'].astype(str)

    fig2 = px.line(monthly, x='order_date', y='total_revenue',
                   markers=True, title="Monthly Revenue Trend")

    fig3 = px.scatter(filtered_df, x='discount_percent', y='total_revenue',
                      color='product_category', size='total_revenue',
                      title="Discount vs Revenue")

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.plotly_chart(fig3, use_container_width=True)

    st.plotly_chart(fig2, use_container_width=True)

    # ================= AI ENGINE =================
    st.markdown("## 🧠 AI Business Analyst")

    top_cat = cat.sort_values('total_revenue', ascending=False).iloc[0]

    insight = f"""
📌 **Top Category:** {top_cat['product_category']}  
💰 **Revenue Leader:** {top_cat['total_revenue']:,.0f}  

📦 Orders Analyzed: {filtered_df.shape[0]}  
⭐ Avg Rating: {filtered_df['rating'].mean():.2f}  

📊 **AI Insight:**  
- Sales performance is strongly driven by top category dominance  
- Discount strategy impacts revenue distribution  
- Region: {region} shows distinct buying behavior
"""

    st.success(insight)

    # ================= EXPORT =================
    st.markdown("## 📥 Export Data")

    csv = filtered_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        "Download CSV Report",
        csv,
        "report.csv",
        "text/csv"
    )

else:
    st.info("👆 Upload Excel file to activate Elite Dashboard")