# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 20:21:44 2026

@author: Shobhit Sharma
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# ---------------- CONFIG ----------------
st.set_page_config(page_title="📊 Stock Analysis Dashboard", layout="wide")

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
st.title("📈 Tech Stock Analysis Dashboard")
st.markdown("Analyze stock trends, returns, and correlations interactively.")

# ---------------- KPI SECTION ----------------
latest_price = company_df['close'].iloc[-1]
avg_price = company_df['close'].mean()
max_price = company_df['close'].max()

col1, col2, col3 = st.columns(3)
col1.metric("💰 Latest Price", f"${latest_price:.2f}")
col2.metric("📊 Average Price", f"${avg_price:.2f}")
col3.metric("🚀 Max Price", f"${max_price:.2f}")

# ---------------- PRICE TREND ----------------
st.subheader("📉 Closing Price Trend")
fig1 = px.line(company_df, x="date", y="close",
               title=f"{selected_company} Closing Prices",
               template="plotly_dark")
st.plotly_chart(fig1, use_container_width=True)

# ---------------- MOVING AVERAGE ----------------
st.subheader("📊 Moving Averages")
for ma in [10, 20, 50]:
    company_df[f"MA_{ma}"] = company_df['close'].rolling(ma).mean()

fig2 = px.line(company_df, x="date",
               y=["close", "MA_10", "MA_20", "MA_50"],
               template="plotly_dark")
st.plotly_chart(fig2, use_container_width=True)

# ---------------- DAILY RETURNS ----------------
st.subheader("📈 Daily Returns (%)")
company_df['Daily Return'] = company_df['close'].pct_change() * 100

fig3 = px.line(company_df, x="date", y="Daily Return",
               template="plotly_dark")
st.plotly_chart(fig3, use_container_width=True)

# ---------------- RESAMPLING ----------------
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
st.subheader("🔥 Correlation Heatmap")

pivot_df = all_data.pivot(index='date', columns='Name', values='close')

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    fig5, ax = plt.subplots(figsize=(5, 3))
    sns.heatmap(pivot_df.corr(), annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    plt.title("Stock Correlation", fontsize=10)
    st.pyplot(fig5, use_container_width=False)

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("💡 *Built with Streamlit, Plotly & Seaborn | Designed for Data Analytics Portfolio by Shobhit Sharma*")
