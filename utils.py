import yfinance as yf
import pandas as pd
import streamlit as st

@st.cache_data
def get_pnl(actions):
    tickers = actions['ticker'].tolist()
    df = yf.download(tickers, period='max')
    close = df['Close']
    def profit(i):
        curr_close = close[actions['ticker'][i]]
        date_idx = curr_close.index.get_indexer([actions['date'][i]], method='nearest')[0]
        close_i = (curr_close - curr_close.iloc[date_idx])
        close_i.loc[close_i.index < actions['date'][i]] = 0
        profit = close_i * actions['qty'][i]
        return profit

    profits = sum(profit(i) for i in range(len(actions)))
    profits = profits[profits.index >= actions['date'].min()]
    return profits

def get_daily_pnl(profits):
    daily_pnl = profits.diff().fillna(0)
    daily_pnl = pd.DataFrame({'profit': daily_pnl})
    daily_pnl['color'] = daily_pnl['profit'].apply(lambda x: 'green' if x >= 0 else 'red')    
    return daily_pnl.reset_index()

@st.cache_data
def get_portfolio(actions):
    actions = actions.drop(columns='date')
    portfolio = actions.groupby('ticker')['qty'].sum().reset_index()
    tickers = portfolio['ticker'].tolist()
    df = yf.download(tickers)
    close = df['Close']
    portfolio['amount'] = portfolio['qty'] * portfolio['ticker'].apply(lambda ticker: close[ticker].iloc[-1])
    portfolio = portfolio.sort_values(by='amount', ascending=False)
    portfolio['amount'] = portfolio['amount'].abs().round(2)
    return portfolio

def filter_portfolio(portfolio):
    portfolio = portfolio.drop(columns='qty')
    mask = portfolio['amount'] / portfolio['amount'].sum() < 0.02
    others = pd.DataFrame({'ticker': ['Others'], 'amount': [portfolio.loc[mask, 'amount'].sum()]})
    portfolio = portfolio[~mask]
    portfolio = pd.concat([portfolio, others], ignore_index=True)
    return portfolio