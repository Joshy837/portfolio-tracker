import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from utils import get_pnl, get_daily_pnl, get_portfolio, filter_portfolio

st.set_page_config(layout="wide")

col1, col2 = st.columns([1, 2])

with col1:
    uploaded_file = st.file_uploader("Upload your orders:", type="csv")

    if uploaded_file is not None:
      actions = pd.read_csv(uploaded_file)
    else:
        actions = pd.DataFrame([
            {"ticker": "AAPL", "date": "2024-06-01", "qty": 1},
            {"ticker": "TSLA", "date": "2024-06-05", "qty": 2},
            {"ticker": "AAPL", "date": "2024-07-01", "qty": -1}
        ])
    actions = st.data_editor(actions, use_container_width=True, num_rows="dynamic")

with col2:
    profits = get_pnl(actions)
    
    tab1, tab2, tab3 = st.tabs(["📈 Cumulative PnL", "📊 Daily PnL", "💼 Portfolio Breakdown"])

    with tab1:
      st.line_chart(profits)
    
    with tab2:
      daily_pnl = get_daily_pnl(profits)
      chart = alt.Chart(daily_pnl).mark_bar().encode(
          x='Date:T',
          y='profit:Q',
          color=alt.Color('color:N', scale=None),
          tooltip=['Date:T', 'profit:Q']
      )
      st.altair_chart(chart, use_container_width=True)
    
    with tab3:
      col1, col2 = st.columns(2)

      with col1:
        portfolio = get_portfolio(actions)
        filtered_portfolio = filter_portfolio(portfolio)
        fig = px.pie(filtered_portfolio, names='ticker', values='amount')
        st.plotly_chart(fig, use_container_width=True)
      
      with col2:
        st.dataframe(portfolio, use_container_width=True)
