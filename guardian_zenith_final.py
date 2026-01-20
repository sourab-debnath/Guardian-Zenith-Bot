import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import os

# 1. Page Configuration
st.set_page_config(page_title="Guardian Zenith Terminal", layout="wide", page_icon="🛡️")

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ GUARDIAN ZENITH: COMMAND CENTER")

# 2. Sidebar & Data Fetching
target_asset = st.sidebar.text_input("Ticker (e.g., BTC-USD)", "BTC-USD").upper()
data = yf.download(target_asset, period="1y", interval="1d", progress=False)

if not data.empty:
    current_price = data['Close'].iloc[-1]
    
    # 3. Strategy Brain (Day 16 Logic)
    def get_brain_data(df):
        # Moving Averages
        f_ma = df['Close'].rolling(window=25).mean().iloc[-1]
        s_ma = df['Close'].rolling(window=30).mean().iloc[-1]
        
        # RSI Calculation
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi_val = 100 - (100 / (1 + (gain / loss).iloc[-1]))
        
        status = "BULLISH 🚀" if f_ma > s_ma else "BEARISH 🛡️"
        risk = "HIGH RISK ⚠️" if rsi_val > 70 else "SAFE ✅"
        return status, rsi_val, risk

    status, rsi, risk = get_brain_data(data)

    # 4. Dashboard Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric(f"Live {target_asset}", f"${current_price:,.2f}")
    m2.metric("Sentinel Sentiment", status)
    m3.metric("RSI Strength", f"{rsi:.2f}", delta=risk)

    # 5. Strategy Time Machine (Backtest)
    st.divider()
    st.subheader("🕰️ Strategy Time Machine (1-Year ROI)")
    
    data['Fast_MA'] = data['Close'].rolling(window=25).mean()
    data['Slow_MA'] = data['Close'].rolling(window=30).mean()
    data['Signal'] = (data['Fast_MA'] > data['Slow_MA']).astype(int)
    data['Strategy_Return'] = data['Signal'].shift(1) * data['Close'].pct_change()
    
    cumulative_roi = (1 + data['Strategy_Return'].fillna(0)).cumprod() - 1
    st.line_chart(cumulative_roi)
    st.metric("Total ROI", f"{cumulative_roi.iloc[-1]*100:.2f}%")
else:
    st.error("Could not fetch data. Please check the ticker symbol.")

