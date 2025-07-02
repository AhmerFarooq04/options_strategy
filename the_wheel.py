import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="The Wheel ☸️", page_icon="☸️")

st.title("The Wheel ☸️")

st.markdown(
    """
    ## The Wheel Strategy

    The Wheel Strategy involves **selling cash‑secured puts** and, if assigned, **selling covered calls** on the shares you now own.  
    It’s popular for generating option‑premium income in sideways‑to‑bullish markets.

    **Cycle:**
    1. *Sell Put ➡️ Maybe Assigned*
    2. *If Assigned ➡️ Own 100 shares*
    3. *Sell Covered Call ➡️ Collect Premium / Possibly Called Away*
    4. *Repeat*

    ---
    
    ### Risk Tolerance Explanation:
    The risk slider adjusts how far from the current price the strategy selects option strikes based on historical monthly price movement quantiles.  
    - Lower risk: Strikes farther away from current price, more conservative but lower premium income.  
    - Higher risk: Strikes closer to current price, higher premium but greater chance of assignment or loss.  
    """
)

stock_ticker = st.text_input("Ticker", "NVDA", key="ticker")

risk_pct = st.slider(
    "Risk tolerance (percentile for strike selection, 0=conservative, 100=aggressive)",
    min_value=0, max_value=100, value=30, step=5, key="risk_pct"
)

# Load price history for the main ticker
def load_price_history(ticker: str) -> pd.Series | None:
    try:
        df = yf.download(tickers=ticker, period="5y", progress=False, auto_adjust=True)

        if df.empty:
            st.error(f"No data found for ticker: {ticker}. Please check the ticker symbol.")
            return None
        
        if "Close" not in df.columns:
            st.error(f"No 'Close' column found for ticker: {ticker}. Data might be incomplete or malformed.")
            return None

        close_series = df["Close"].copy()
        close_series.name = ticker
        return close_series

    except Exception as exc:
        st.error(f"Data download failed for {ticker}: {exc}. Please check your internet connection or the ticker symbol.")
        return None

close_prices = load_price_history(stock_ticker)
if close_prices is None:
    st.stop()

last_price = float(close_prices.iloc[-1])

monthly = close_prices.resample("ME").last()

if isinstance(monthly, pd.Series):
    monthly = monthly.to_frame(name="price")
else:
    monthly.rename(columns={monthly.columns[0]: "price"}, inplace=True)
    
monthly["prev"] = monthly["price"].shift(1)
monthly.dropna(inplace=True)
monthly["pct_change"] = (monthly["price"] / monthly["prev"] - 1) * 100

# Monthly return distribution histogram
hist_fig = go.Figure()
hist_fig.add_trace(
    go.Histogram(
        x=monthly["pct_change"],
        nbinsx=15,
        marker=dict(color="rgba(57,255,20,0.4)", line=dict(color="#39FF14", width=2)),
    )
)
hist_fig.update_layout(
    title="Monthly Percent‑Change Distribution",
    paper_bgcolor="#0e1117",
    plot_bgcolor="#0e1117",
    font=dict(color="#FFFFFF"),
    xaxis=dict(title="% Change", gridcolor="#444444"),
    yaxis=dict(title="Frequency", gridcolor="#444444"),
    bargap=0.03,
)

st.plotly_chart(hist_fig, use_container_width=True)

# Add box plot below histogram
box_fig = go.Figure()
box_fig.add_trace(
    go.Box(
        y=monthly["pct_change"],
        boxpoints="all",  # show all points
        jitter=0.5,
        whiskerwidth=0.2,
        marker=dict(color="#39FF14"),
        line=dict(color="#39FF14"),
        name="Monthly % Change",
        boxmean=True,
    )
)
box_fig.update_layout(
    title="Box Plot of Monthly Percent‑Change",
    paper_bgcolor="#0e1117",
    plot_bgcolor="#0e1117",
    font=dict(color="#FFFFFF"),
    yaxis=dict(title="% Change", gridcolor="#444444"),
)

st.plotly_chart(box_fig, use_container_width=True)

# 6-month rolling volatility
monthly["volatility"] = monthly["pct_change"].rolling(window=6).std()

vol_fig = go.Figure()
vol_fig.add_trace(
    go.Scatter(
        x=monthly.index,
        y=monthly["volatility"],
        mode="lines+markers",
        line=dict(color="#39FF14"),
        marker=dict(size=5),
        name="6-Month Rolling Volatility (%)",
    )
)
vol_fig.update_layout(
    title="6-Month Rolling Volatility of Monthly Returns",
    paper_bgcolor="#0e1117",
    plot_bgcolor="#0e1117",
    font=dict(color="#FFFFFF"),
    xaxis=dict(title="Date", gridcolor="#444444"),
    yaxis=dict(title="Volatility (%)", gridcolor="#444444"),
)

st.plotly_chart(vol_fig, use_container_width=True)

def map_put_quantile(risk):
    if risk <= 10:
        return 0.05
    else:
        return 0.05 + ((risk - 10) / 90) * (0.50 - 0.05)

def map_call_quantile(risk):
    if risk <= 10:
        return 0.95
    else:
        return 0.95 - ((risk - 10) / 90) * (0.95 - 0.50)

put_quantile = map_put_quantile(risk_pct)
call_quantile = map_call_quantile(risk_pct)

put_quantile = max(0.01, min(put_quantile, 0.99))
call_quantile = max(0.01, min(call_quantile, 0.99))

put_pct = monthly["pct_change"].quantile(put_quantile) / 100
call_pct = monthly["pct_change"].quantile(call_quantile) / 100

put_target = last_price * (1 + put_pct)
call_target = last_price * (1 + call_pct)

try:
    ticker_obj = yf.Ticker(stock_ticker)
    option_dates = ticker_obj.options
except Exception as exc:
    st.error(f"Option chain unavailable: {exc}")
    st.stop()

next_month_start = (pd.Timestamp.now() + pd.offsets.MonthBegin()).normalize()
expiry_date = next((d for d in option_dates if pd.Timestamp(d) >= next_month_start), None)

if expiry_date is None:
    st.error("No suitable expiry found.")
    st.stop()

st.info(f"Using expiry **{expiry_date}**  (≥ first business day next month)")

option_chain = ticker_obj.option_chain(expiry_date)
calls_df, puts_df = option_chain.calls, option_chain.puts

# Find closest call strike available
call_strike = calls_df["strike"].iloc[(calls_df["strike"] - call_target).abs().argmin()]

# Find closest put strike available
put_strike = puts_df["strike"].iloc[(puts_df["strike"] - put_target).abs().argmin()]

call_option = calls_df[calls_df["strike"] == call_strike]
put_option = puts_df[puts_df["strike"] == put_strike]

if call_option.empty or put_option.empty:
    st.error("Selected strikes not in chain – try adjusting risk tolerance.")
    st.stop()

call_premium = float(call_option["lastPrice"].iloc[0])
put_premium = float(put_option["lastPrice"].iloc[0])

total_premium = 100 * (call_premium + put_premium)
required_capital = 100 * put_strike
monthly_return_pct = total_premium / required_capital * 100
annualized_return = monthly_return_pct * 12  # annualized % return (simple)

st.subheader("Strategy Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Capital Required", f"${required_capital:,.0f}")
col2.metric("Total Premium", f"${total_premium:,.0f}")
col3.metric("Monthly % Return", f"{monthly_return_pct:.2f}%")

st.metric("Annualised Return (simple)", f"{annualized_return:.2f}%")
