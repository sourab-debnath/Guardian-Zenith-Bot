import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Page & Layout Config
st.set_page_config(
    page_title="Guardian Zenith Terminal",
    layout="wide",
    page_icon="🛡️"
)

st.markdown("""
<style>
.main { background-color: #0e1117; }
div[data-testid="stMetricValue"] {
    font-size: 1.8rem;
    color: #00d4ff;
}
</style>
""", unsafe_allow_html=True)

st.title("🛡️ GUARDIAN ZENITH: COMMAND CENTER")

# 2. Market Selection Sidebar
target_asset = st.sidebar.text_input(
    "Ticker (e.g., BTC-USD)",
    "BTC-USD"
).upper()

# 3. Data Fetching
data = yf.download(
    target_asset,
    period="1y",
    interval="1d",
    progress=False
)

# =========================
# STRATEGY BRAIN (FIXED)
# =========================
def get_brain_data(df):
    if df.empty or len(df) < 30:
        return "NOT ENOUGH DATA", 0.0, "UNKNOWN"

    # Moving Averages
    fast_ma = df['Close'].rolling(25).mean()
    slow_ma = df['Close'].rolling(30).mean()

    # RSI Calculation
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    # 🔑 Extract LAST values (THIS FIXES THE ERROR)
    latest_fast = fast_ma.iloc[-1]
    latest_slow = slow_ma.iloc[-1]
    latest_rsi = rsi.iloc[-1]

    # Decision Logic
    status = "BULLISH 🚀" if latest_fast > latest_slow else "BEARISH 🛡️"
    risk = "HIGH RISK ⚠️" if latest_rsi > 70 or latest_rsi < 30 else "SAFE ✅"

    return status, latest_rsi, risk


if not data.empty:
    status, rsi, risk = get_brain_data(data)
    current_price = data['Close'].iloc[-1]

    # 4. Dashboard Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric(f"Live {target_asset}", f"${current_price:,.2f}")
    m2.metric("Sentinel Sentiment", status)
    m3.metric("RSI Strength", f"{rsi:.2f}", delta=risk)

    # 5. Strategy Time Machine (Backtest)
    st.divider()
    st.subheader("🕰️ Strategy Time Machine (1-Year Performance)")

    data['Signal'] = (
        data['Close'].rolling(25).mean()
        > data['Close'].rolling(30).mean()
    ).astype(int)

    data['Returns'] = data['Signal'].shift(1) * data['Close'].pct_change()
    cumulative_roi = (1 + data['Returns'].fillna(0)).cumprod() - 1

    st.line_chart(cumulative_roi, use_container_width=True)
    st.metric("Total ROI", f"{cumulative_roi.iloc[-1] * 100:.2f}%")

else:
    st.error("Please enter a valid ticker symbol in the sidebar.")
