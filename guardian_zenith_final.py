import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import os

# 1. Page Configuration
st.set_page_config(page_title="Guardian Zenith Terminal", layout="wide", page_icon="🛡️")

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ GUARDIAN ZENITH: COMMAND CENTER")

# 2. Sidebar Navigation
st.sidebar.header("📡 Market Watch")
target_asset = st.sidebar.text_input("Ticker (e.g., BTC-USD)", "BTC-USD").upper()
LOG_FILE = "trade_history.csv"

# 3. Memory Initialization
if 'balance' not in st.session_state:
    st.session_state.balance, st.session_state.position = 10000.0, 0.0

# 4. Data & Logic Engine
# Pulling 1 year of data for both the Brain and the Time Machine
data = yf.download(target_asset, period="1y", interval="1d", progress=False)

if not data.empty:
    current_price = data['Close'].iloc[-1]

    def get_brain_data(df):
        # Calculate Moving Averages
        f_ma_series = df['Close'].rolling(window=25).mean()
        s_ma_series = df['Close'].rolling(window=30).mean()
        
        # Calculate RSI
        d = df['Close'].diff()
        g = (d.where(d > 0, 0)).rolling(14).mean()
        l = (-d.where(d < 0, 0)).rolling(14).mean()
        rsi_series = 100 - (100 / (1 + (g / l)))
        
        # --- FIXED LOGIC: Get single values for the current moment ---
        f_ma = f_ma_series.iloc[-1]
        s_ma = s_ma_series.iloc[-1]
        rsi_val = rsi_series.iloc[-1]
        
        # Now these comparisons work because they are number vs number
        status = "BULLISH 🚀" if f_ma > s_ma else "BEARISH 🛡️"
        risk = "HIGH RISK ⚠️" if rsi_val > 70 else "SAFE ✅"
        
        return status, rsi_val, risk

    status, rsi, risk = get_brain_data(data)

    # 5. Virtual Trading logic
    if status == "BULLISH 🚀" and st.session_state.balance > 0:
        st.session_state.position, st.session_state.balance = st.session_state.balance / current_price, 0
    elif status == "BEARISH 🛡️" and st.session_state.position > 0:
        st.session_state.balance, st.session_state.position = st.session_state.position * current_price, 0

    # 6. UI Metrics Row
    current_val = st.session_state.balance if st.session_state.balance > 0 else st.session_state.position * current_price
    profit = current_val - 10000

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(f"Live {target_asset}", f"${current_price:,.2f}")
    m2.metric("Sentinel Sentiment", status)
    m3.metric("RSI Strength", f"{rsi:.2f}", delta=risk)
    m4.metric("Vault Balance", f"${current_val:,.2f}", delta=f"${profit:,.2f}")

    # 7. Strategy Time Machine (Backtest Visual)
    st.divider()
    st.subheader("🕰️ Strategy Time Machine (1-Year Performance)")
    
    data['Fast_MA'] = data['Close'].rolling(window=25).mean()
    data['Slow_MA'] = data['Close'].rolling(window=30).mean()
    data['Signal'] = (data['Fast_MA'] > data['Slow_MA']).astype(int)
    data['Daily_Return'] = data['Close'].pct_change()
    data['Strategy_Return'] = data['Signal'].shift(1) * data['Daily_Return']
    
    cumulative_roi = (1 + data['Strategy_Return'].fillna(0)).cumprod() - 1
    st.line_chart(cumulative_roi, use_container_width=True)
else:
    st.error("Invalid Ticker or No Data Found.")
