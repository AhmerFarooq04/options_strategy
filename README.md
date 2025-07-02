# ☸️ The Wheel Strategy Simulator

A modern, interactive Streamlit app to simulate and visualize **The Wheel Options Strategy** with real-time data from Yahoo Finance. Designed for beginner to intermediate options traders, this tool helps you evaluate potential monthly income, visualize historical return distributions, and model future price paths using Monte Carlo simulations.

---

## 📈 What is the Wheel Strategy?

The Wheel Strategy is a conservative income-focused options trading approach. The process involves:

1. **Sell Cash-Secured Put**  
   - If the stock stays **above** the strike: keep the premium.
   - If the stock drops **below** the strike: you're assigned 100 shares.

2. **Sell Covered Call**  
   - If the stock stays **below** the strike: keep the premium and repeat.
   - If the stock rises **above** the strike: shares get called away (sold).

This repeats like a "wheel" — continuously collecting option premiums in sideways-to-bullish markets.

---

## 🧠 Key Features

| Feature                            | Description |
|------------------------------------|-------------|
| 📊 **Historical Returns Analysis** | Visualize monthly price change distributions and rolling volatility. |
| ⚙️ **Risk-Based Strike Selection** | Choose strike prices based on historical percent-change quantiles. |
| 💸 **Live Premium Quotes**         | Fetches real option prices from Yahoo Finance for next-month expiry. |
| 🎲 **Monte Carlo Simulation**      | Runs 200+ GBM-based price path simulations to estimate outcome probabilities. |
| 💵 **Return Metrics**              | Calculates total premium, capital required, and projected returns. |

---

## 🖼️ App Preview

### 📈 Historical Monthly Return Distribution

![Histogram of Returns](https://github.com/user-attachments/assets/5980779b-0391-4ee0-9f2b-f084e45260f1)

---

### 📉 6-Month Rolling Volatility

![Volatility Chart](https://github.com/user-attachments/assets/599eed2f-81cc-4f28-a037-26e3ea83741f)


---

### 📊 Monte Carlo Simulation Paths

![Monte Carlo Simulation](https://github.com/user-attachments/assets/5a733d75-763e-4553-bb7f-562b96bb7339)

---

## Check it out 
https://optionsstrategy-thewheel.streamlit.app/

----

## ⚙️ How to Run Locally

### 🔧 Prerequisites

- Python 3.9+
- `pip` package manager

### 📦 Install Dependencies

```bash
pip install streamlit yfinance pandas plotly numpy


