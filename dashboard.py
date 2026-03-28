# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 20:21:44 2026

@author: Shobhit Sharma
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- CONFIG ----------------
st.set_page_config(page_title="📊 Stock Analysis Dashboard", layout="wide")

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Main background */
.stApp {
    background: linear-gradient(135deg, #020617, #0f172a);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #020617 !important;
}

/* Metric Cards */
div[data-testid="metric-container"] {
    background-color: #111827;
    border: 1px solid #1f2937;
    padding: 15px;
    border-radius: 14px;
    box-shadow: 0px 4px 25px rgba(0,0,0,0.6);
}

/* Remove white padding */
.block-container {
    padding-top: 2rem;
}

/* Headings */
h1, h2, h3 {
    color: #e5e7eb;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
file_paths = {
    "AMZN": r"individual_stocks_5yr/AMZN_data.csv",
    "AAPL": r"individual_stocks_5yr/AAPL_data.csv",
    "GOOG": r"individual_stocks_5yr/GOOG_data.csv",
    "MSFT": r"individual_stocks_5yr/MSFT_data.csv",
}

@st.cache_data
def load_data():
    df_list = []
    for name, path in file_paths.items():
        df = pd.read_csv(path)
        df['Name'] = name
        df_list.append(df)
    data = pd.concat(df_list, ignore_index=True)
    data['date'] = pd.to_datetime(data['date'])
    return data

all_data = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.title("📌 Controls")
selected_company = st.sidebar.selectbox("Select Company", list(file_paths.keys()))

# ---------------- FILTER DATA ----------------
company_df = all_data[all_data['Name'] == selected_company].copy()
company_df = company_df.sort_values('date')

# ---------------- HEADER ----------------
st.markdown("""
<div style='text-align:center; padding: 20px 0 10px 0;'>
    <h1 style='font-size:48px; margin-bottom:5px;'>📊 Tech Stock Analysis Dashboard</h1>
    <p style='color:#9ca3af; font-size:18px;'>
        Analyze stock trends, returns, and correlations interactively
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------- KPI SECTION ----------------
st.markdown("---")
latest_price = company_df['close'].iloc[-1]
avg_price = company_df['close'].mean()
max_price = company_df['close'].max()

kpi1, kpi2, kpi3 = st.columns(3)

kpi1.markdown(f"""
<div style='
    background: rgba(17, 25, 40, 0.75);
    padding: 20px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
'>
    <p style='color:#9ca3af;'>💰 Latest Price</p>
    <h2>${latest_price:.2f}</h2>
</div>
""", unsafe_allow_html=True)

kpi2.markdown(f"""
<div style='
    background: rgba(17, 25, 40, 0.75);
    padding: 20px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
'>
    <p style='color:#9ca3af;'>📊 Average Price</p>
    <h2>${avg_price:.2f}</h2>
</div>
""", unsafe_allow_html=True)

kpi3.markdown(f"""
<div style='
    background: rgba(17, 25, 40, 0.75);
    padding: 20px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
'>
    <p style='color:#9ca3af;'>🚀 Max Price</p>
    <h2>${max_price:.2f}</h2>
</div>
""", unsafe_allow_html=True)

# ---------------- PRICE TREND ----------------

st.markdown("---")

st.subheader("📉 Closing Price Trend")
fig1 = px.line(company_df, x="date", y="close",
               title=f"{selected_company} Closing Prices",
               template="plotly_dark")
st.plotly_chart(fig1, use_container_width=True)

# ---------------- MOVING AVERAGE ----------------
st.markdown("---")
st.subheader("📊 Moving Averages")
for ma in [10, 20, 50]:
    company_df[f"MA_{ma}"] = company_df['close'].rolling(ma).mean()

fig2 = px.line(company_df, x="date",
               y=["close", "MA_10", "MA_20", "MA_50"],
               template="plotly_dark")
st.plotly_chart(fig2, use_container_width=True)

# ---------------- DAILY RETURNS ----------------

st.markdown("---")
st.subheader("📈 Daily Returns (%)")
company_df['Daily Return'] = company_df['close'].pct_change() * 100

fig3 = px.line(company_df, x="date", y="Daily Return",
               template="plotly_dark")
st.plotly_chart(fig3, use_container_width=True)

# ---------------- RESAMPLING ----------------
st.markdown("---")
st.subheader("📅 Resampled Prices")
resample_option = st.radio("Frequency", ["Monthly", "Quarterly", "Yearly"], horizontal=True)

company_df.set_index('date', inplace=True)

if resample_option == "Monthly":
    resampled = company_df['close'].resample('M').mean()
elif resample_option == "Quarterly":
    resampled = company_df['close'].resample('Q').mean()
else:
    resampled = company_df['close'].resample('Y').mean()

fig4 = px.line(resampled, title=f"{resample_option} Avg Closing Price", template="plotly_dark")
st.plotly_chart(fig4, use_container_width=True)

# ---------------- CORRELATION HEATMAP ----------------
# ---------------- CORRELATION HEATMAP ----------------

st.markdown("---")
st.subheader("🔥 Correlation Heatmap")

pivot_df = all_data.pivot(index='date', columns='Name', values='close')
corr = pivot_df.corr()

fig5 = px.imshow(
    corr,
    text_auto=True,
    color_continuous_scale='RdBu_r',
    title="Stock Correlation Heatmap"
)

st.plotly_chart(fig5, use_container_width=True)

# ---------------- FOOTER ----------------
st.markdown("""
---
<div style='text-align:center; color:#6b7280; font-size:14px;'>
Built with Streamlit & Plotly | Portfolio Project by <b>Shobhit Sharma</b>
</div>
""", unsafe_allow_html=True)
