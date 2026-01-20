import streamlit as st
import yfinance as yf
import pandas as pd
import os

# 1. Page & Layout Config
st.set_page_config(page_title="Guardian Zenith Terminal", layout="wide", page_icon="🛡️")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ GUARDIAN ZENITH: COMMAND CENTER")

# 2. Market Selection Sidebar
target_asset = st.sidebar.text_input("Ticker (e.g., BTC-USD)", "BTC-USD").upper()

# 3. Data Fetching (Pulling 1 year for the Time Machine)
data = yf.download(target_asset, period="1y", interval="1d", progress=False)

if not data.empty:
    # 4. Strategy Brain (Day 16 Logic)
    def get_brain_data(df):
        # Calculate Signals
        f_ma_line = df['Close'].rolling(window=25).mean()
        s_ma_line = df['Close'].rolling(window=30).mean()
        
        # Calculate RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi_line = 100 - (100 / (1 + (gain / loss)))
        
        # FIXED: Extracting single most recent values using .iloc[-1]
        latest_f_ma = f_ma_line.iloc[-1]
        latest_s_ma = s_ma_line.iloc[-1]
        latest_rsi = rsi_line.iloc[-1]
        
        # Comparison logic
        status = "BULLISH 🚀" if latest_f_ma > latest_s_ma else "BEARISH 🛡️"
        risk = "HIGH RISK ⚠️" if latest_rsi > 70 or latest_rsi < 30 else "SAFE ✅"
        
        return status, latest_rsi, risk

    status, rsi, risk = get_brain_data(data)
    current_price = data['Close'].iloc[-1]

    # 5. Dashboard Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric(f"Live {target_asset}", f"${current_price:,.2f}")
    m2.metric("Sentinel Sentiment", status)
    m3.metric("RSI Strength", f"{rsi:.2f}", delta=risk)

    # 6. Strategy Time Machine (Backtest)
    st.divider()
    st.subheader("🕰️ Strategy Time Machine (1-Year Performance)")
    
    # Logic for the backtest chart
    data['Strategy_Signal'] = (data['Close'].rolling(25).mean() > data['Close'].rolling(30).mean()).astype(int)
    data['Returns'] = data['Strategy_Signal'].shift(1) * data['Close'].pct_change()
    cumulative_roi = (1 + data['Returns'].fillna(0)).cumprod() - 1
    
    st.line_chart(cumulative_roi, use_container_width=True)
    st.metric("Total ROI", f"{cumulative_roi.iloc[-1]*100:.2f}%")

else:
    st.error("Please enter a valid ticker symbol in the sidebar.")
