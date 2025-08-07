# streamlit_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import re
from datetime import datetime

st.set_page_config(page_title="Trade Dashboard", layout="wide")

# Load trade results
try:
    df = pd.read_csv("trade_results.csv")
except FileNotFoundError:
    st.error("❌ 'trade_results.csv' not found. Please run main.py first.")
    st.stop()
df['timestamp'] = pd.to_datetime(df['timestamp'])

#  Date Range Selector
st.subheader("Filter by Date Range")
min_date = df['timestamp'].min().date()
max_date = df['timestamp'].max().date()

start_date, end_date = st.date_input(
    "Select a date range:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Convert selected dates to full datetime bounds
start_datetime = datetime.combine(start_date, datetime.min.time())
end_datetime = datetime.combine(end_date, datetime.max.time())

# Filter the DataFrame
df = df[(df['timestamp'] >= start_datetime) & (df['timestamp'] <= end_datetime)]

st.title("📊 Trade Signal Dashboard")
st.markdown("Insights from processed Telegram trading signals")

# Drop rows with missing P/L
df.dropna(subset=["pl"], inplace=True)

# ✅ Clean symbol suffixes
def clean_symbol(sym):
    return re.sub(r'[^\w]+$', '', sym).rstrip('M')

df["symbol"] = df["symbol"].apply(clean_symbol)

# KPIs
total_signals = len(df)
wins = df[df["result"] == "win"]
losses = df[df["result"] == "loss"]
win_rate = 100 * len(wins) / total_signals if total_signals else 0
avg_win = wins["pl"].mean() if not wins.empty else 0
avg_loss = losses["pl"].mean() if not losses.empty else 0
most_traded_pair = df["symbol"].mode()[0] if not df.empty else "N/A"

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("📨 Total Signals", total_signals)
col2.metric("✅ Win Rate (%)", f"{win_rate:.2f}")
col3.metric("📈 Avg Win", f"{avg_win:.4f}")
col4.metric("📉 Avg Loss", f"{avg_loss:.4f}")
col5.metric("💱 Most Traded Pair", most_traded_pair)

# Profit/Loss Histogram
st.subheader("📊 Profit/Loss Distribution")
fig = px.histogram(df, x="pl", nbins=40, title="Trade Profit/Loss Histogram", labels={"pl": "Profit/Loss"})
st.plotly_chart(fig, use_container_width=True)

# Best & Worst Trades
st.subheader("🏆 Best & Worst Trades")
best_trade = df.loc[df["pl"].idxmax()]
worst_trade = df.loc[df["pl"].idxmin()]

col1, col2 = st.columns(2)
with col1:
    st.metric("Best Trade", f"{best_trade['symbol']} {best_trade['type']} → {best_trade['pl']:.2f}")
with col2:
    st.metric("Worst Trade", f"{worst_trade['symbol']} {worst_trade['type']} → {worst_trade['pl']:.2f}")

# Show Raw Table
st.subheader("📋 All Trades")
st.dataframe(df.sort_values("timestamp", ascending=False).reset_index(drop=True))
