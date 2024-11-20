import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np
import seaborn as sns

# Title and description
st.title("The Wheel ☸️ ")
st.markdown(
    """
    ## The Wheel Strategy

    The Wheel Strategy is an options trading strategy that involves selling cash-secured puts and covered calls to generate consistent income with relatively low risk, particularly in stable or bullish market conditions.

    ## Here's how it works:

    1. **Sell a Cash-Secured Put**: Say there is a stock you want to own , in our case we take NVIDIA but you think its overvalued so you sell aput at the price you want to buy it at and collect the premium

    2. **If the Put is Assigned**: theres two options at experiery either NVDA reaches the strike or not if it doesnt go back to step 1 if not congrats you own a hundred shares of NVDA

    3. **Sell Covered Calls**: After owning the stock, you sell call options on the stock to collect premiums and you place the strike sufficiently high so you know you will profit .

    4. **Repeat the Process**: The cycle repeats as long as the stock remains profitable and the options are profitable to sell.

    """
)

# User inputs
stock = st.text_input("Enter Stock Ticker:", "NVDA", key="stock_input")
quantile_upper = st.slider("Quantile Upper Bound (0-1)",
                           0.5, 1.0, 0.8, key="upper_quantile")
quantile_lower = st.slider("Quantile Lower Bound (0-1)",
                           0.0, 0.5, 0.15, key="lower_quantile")

@st.cache_data
def get_stock_data(stock):
    try:
        data = yf.download(stock, period="5y") 
        return data
    except Exception as e:
        st.error(f"Error downloading stock data: {e}")
        return None


stock_yf = yf.Ticker(stock)
data = get_stock_data(stock)

if data is not None:
    close = data.loc[:, "Close"].copy()
    last_price = close.iloc[-1]

    
    monthly_close = close.resample('ME').last()
    monthly_df = monthly_close.reset_index()
    monthly_df.columns = ['Date', 'price']
    monthly_df["prev_month_price"] = monthly_df["price"].shift(1)
    monthly_df.dropna(inplace=True)
    monthly_df["monthly_percent_change"] = ((monthly_df["price"] - monthly_df["prev_month_price"]) / monthly_df["prev_month_price"]).mul(100)

   
    mean_value = monthly_df["monthly_percent_change"].mean()
    std_dev_value = monthly_df["monthly_percent_change"].std()

    
    sns.histplot(monthly_df["monthly_percent_change"], kde=True, bins=15, color='skyblue', edgecolor='black')
    plt.title("Histogram of Monthly Percent Change", fontsize=16, fontweight='bold')
    plt.xlabel("% Change by Month", fontsize=12)
    plt.ylabel("Density", fontsize=12)
    st.pyplot(plt.gcf())

   
    p_upper_value = monthly_df["monthly_percent_change"].quantile(quantile_upper)
    p_lower_value = monthly_df["monthly_percent_change"].quantile(quantile_lower)
    p_upper = math.ceil(p_upper_value)
    p_lower = math.floor(p_lower_value)

  
    exp_call_strike = last_price + ((last_price * p_upper) / 100)
    exp_put_strike = last_price + ((last_price * p_lower) / 100)

   
    available_dates = stock_yf.options
    today = pd.Timestamp.today()
    close_to = today + pd.offsets.MonthBegin(1)

    expiration_date = None
    for i in available_dates:
        if pd.Timestamp(i) >= close_to:
            expiration_date = i
            break

    if expiration_date:
        st.write(f"Selected expiration date: {expiration_date}")

        option_chain = stock_yf.option_chain(str(expiration_date))
        calls = option_chain.calls
        puts = option_chain.puts
        strike_prices = option_chain.calls["strike"]
        difference = strike_prices.iloc[2] - strike_prices.iloc[1]
        call_strike = round(exp_call_strike / difference) * difference
        put_strike = round(exp_put_strike / difference) * difference

        call_strike = float(call_strike)
        put_strike = float(put_strike)

       
        call_prices = calls[calls["strike"] == call_strike]
        put_prices = puts[puts["strike"] == put_strike]

        if not call_prices.empty and not put_prices.empty:
            call_price = call_prices["lastPrice"].iloc[0]
            put_price = put_prices["lastPrice"].iloc[0]
            call_premium = call_price * 100
            put_premium = put_price * 100

            max_profit = call_premium + put_premium
            capital_requirement = put_strike * 100
            percent_profitability = (max_profit / capital_requirement) * 100
            annualized_ret = max_profit * 12

            
            st.markdown(f"# **Strategy Results**")
            st.markdown(f"### **Capital Requirement:** ${capital_requirement:.2f}")
            st.markdown(f"### **Percent Profitability:** {percent_profitability:.2f}%")
            st.markdown(f"### **Max Profit:** ${max_profit:.2f}")
            st.markdown(f"### **Annualized Return:** ${annualized_ret:.2f}")
        else:
            st.error("No matching strike prices found in the option chain.")
    else:
        st.error("No valid expiration date found.")