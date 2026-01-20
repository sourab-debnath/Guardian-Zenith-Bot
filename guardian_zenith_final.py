%%writefile guardian_zenith_final.py
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import os

# 1. Page & Theme Configuration
st.set_page_config(page_title="Guardian Zenith Terminal", layout="wide", page_icon="🛡️")

# Custom CSS for a "Premium" Dark Feel
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #00d4ff; }
    div[data-testid="stMetricDelta"] { font-size: 1rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #1e2130; border-radius: 5px; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ GUARDIAN ZENITH: COMMAND CENTER")

# 2. Sidebar Navigation & Market Watch
st.sidebar.header("📡 Market Watch")
target_asset = st.sidebar.text_input("Ticker (e.g., BTC-USD, ETH-USD)", "BTC-USD").upper()
LOG_FILE = "trade_history.csv"

# 3. Memory & Vault Initialization
if 'balance' not in st.session_state:
    st.session_state.balance, st.session_state.position = 10000.0, 0.0
    st.session_state.trade_history = []

# 4. Data & Logic Engine
data = yf.download(target_asset, period="5d", interval="1h", progress=False)
current_price = data['Close'].iloc[-1]

def get_brain_data(df):
    f_ma = df['Close'].rolling(window=25).mean().iloc[-1]
    s_ma = df['Close'].rolling(window=30).mean().iloc[-1]
    d = df['Close'].diff()
    g, l = (d.where(d > 0, 0)).rolling(14).mean(), (-d.where(d < 0, 0)).rolling(14).mean()
    rsi_val = 100 - (100 / (1 + (g / l).iloc[-1]))
    status = "BULLISH 🚀" if f_ma > s_ma else "BEARISH 🛡️"
    risk = "HIGH RISK ⚠️" if rsi_val > 70 else "SAFE ✅"
    return status, rsi_val, risk

status, rsi, risk = get_brain_data(data)

# 5. Virtual Trading Logic
if status == "BULLISH 🚀" and st.session_state.balance > 0:
    st.session_state.position, st.session_state.balance = st.session_state.balance / current_price, 0
elif status == "BEARISH 🛡️" and st.session_state.position > 0:
    st.session_state.balance, st.session_state.position = st.session_state.position * current_price, 0

# 6. UI: KPI Metrics Row
current_val = st.session_state.balance if st.session_state.balance > 0 else st.session_state.position * current_price
profit = current_val - 10000

m1, m2, m3, m4 = st.columns(4)
m1.metric(f"Live {target_asset}", f"${current_price:,.2f}")
m2.metric("Sentinel Sentiment", status)
m3.metric("RSI Strength", f"{rsi:.2f}", delta=risk)
m4.metric("Vault Balance", f"${current_val:,.2f}", delta=f"${profit:,.2f}")

# 7. UI: Main Area Tabs (UPGRADED FOR DAY 16)
tab1, tab2, tab3 = st.tabs(["📈 Market Visuals", "📜 Permanent Logs", "📰 Intelligence Feed"])

with tab1:
    st.subheader("📈 Price Action & 🕰️ Strategy Time Machine")
    
    # --- DAY 16: 1-Year Backtest Logic ---
    test_data = yf.download(target_asset, period="1y", interval="1d", progress=False)
    test_data['Fast_MA'] = test_data['Close'].rolling(window=25).mean()
    test_data['Slow_MA'] = test_data['Close'].rolling(window=30).mean()
    
    # Calculate Returns
    test_data['Signal'] = (test_data['Fast_MA'] > test_data['Slow_MA']).astype(int)
    test_data['Daily_Return'] = test_data['Close'].pct_change()
    test_data['Strategy_Return'] = test_data['Signal'].shift(1) * test_data['Daily_Return']
    
    cumulative_roi = (1 + test_data['Strategy_Return'].fillna(0)).cumprod() - 1
    final_roi_pct = cumulative_roi.iloc[-1] * 100
    
    # UI Layout for Backtest
    c1, c2 = st.columns([1, 3])
    with c1:
        st.metric("1-Year Strategy ROI", f"{final_roi_pct:.2f}%")
        st.caption("Strategy: 25/30 Day MA Cross")
    with c2:
        st.line_chart(cumulative_roi, use_container_width=True)
    
    st.divider()
    st.subheader("Live 5-Day Price Action")
    st.line_chart(data['Close'], use_container_width=True)

with tab2:
    st.subheader("Trade History (CSV)")
    if os.path.exists(LOG_FILE):
        st.dataframe(pd.read_csv(LOG_FILE), use_container_width=True, hide_index=True)
    else:
        st.info("No trades recorded in current folder yet.")

with tab3:
    st.subheader("Global News Intelligence")
    ticker = yf.Ticker(target_asset)
    for news in ticker.news[:4]:
        with st.expander(f"📌 {news['title']}"):
            st.write(f"**Publisher:** {news['publisher']}")
            st.link_button("View Full Report", news['link'])
