import numpy as np
import pandas as pd
from datetime import date
import streamlit as st
from st_pages import Page, show_pages, add_page_title
import altair as alt
import yfinance as yf
import math 
import streamlit_card as st_card
from streamlit_card import card
from streamlit_extras.stylable_container import stylable_container 
from streamlit_extras.switch_page_button import switch_page 
from streamlit_extras.metric_cards import style_metric_cards
import random

#####################
# Main Page Content #
#####################

with stylable_container(
                key="restart_button",
                css_styles="""
                    button {
                        background-color: SteelBlue;
                        color: white;
                        border-radius: 30px;
                        height: 55px;
                        width: 250px;
                    }
                    """,
            ):
            restart = st.button('Restart the simulation',key='restart_button')

if restart:
    for key in st.session_state.keys():
        del st.session_state[key]
    switch_page('Initialization')

st.divider()

returnRate = st.session_state['tradeRecord']['netProfit'][len(st.session_state['tradeRecord'])-1] / st.session_state['initMoney']

col1, col2 = st.columns(2)

with col1:
    st.image('img/TrophyCup.jpg')

with col2:
    st.markdown("""
            <h1 style='text-align: center; color: Black;'>
              Initial Capital: $""" + str(round(st.session_state['initMoney'],2)) + """
            </h1>
            """, unsafe_allow_html=True)
    st.markdown("""
            <h1 style='text-align: center; color: Black;'>
              NetProfit: $""" + str(round(st.session_state['tradeRecord']['netProfit'][len(st.session_state['tradeRecord'])-1],2)) + 
              """ ( """ + str(format(returnRate, ".2%")) + """ )
            </h1>
            """, unsafe_allow_html=True)
    
st.divider()

st.title('Your performance:')
    
tradeRecord_aggDaily = st.session_state['tradeRecord'].groupby('period').agg({
    'netProfit' : 'sum'
}).reset_index()

tradeRecord_aggDaily['zero'] = tradeRecord_aggDaily['period']*0

st.altair_chart(
    alt.Chart(tradeRecord_aggDaily).mark_line().encode(
    alt.X('period', axis=alt.Axis(labelAngle=-30, values=tradeRecord_aggDaily['period'].to_list()), scale=alt.Scale(domain=[0, st.session_state['len']-1])).title('Simulation Period'),
    alt.Y('netProfit',scale=alt.Scale(domain=[
        min(tradeRecord_aggDaily['netProfit'].values)-1,
        max(tradeRecord_aggDaily['netProfit'].values)+1])).title('Net Profit')
        ) + 
        alt.Chart(tradeRecord_aggDaily).mark_rule(color='green',strokeDash=[2,1]).encode(
    y=alt.datum(0))
        , 
    use_container_width=True)

st.title('Stock performance:')

st.altair_chart(
        alt.Chart(st.session_state['stockData']).mark_line().encode(
        alt.X('Date', axis=alt.Axis(labelAngle=-30)).title(''),
        alt.Y('Adj Close',scale=alt.Scale(domain=[
            min(st.session_state['stockData']['Adj Close'].values)-0.5,
            max(st.session_state['stockData']['Adj Close'].values)+0.5])).title('')
            )+
        alt.Chart(st.session_state['stockData']).mark_circle(size=100).encode(
        alt.X('Date', axis=alt.Axis(labelAngle=-30)).title(''),
        alt.Y('Adj Close',scale=alt.Scale(domain=[
            min(st.session_state['stockData']['Adj Close'].values)-0.5,
            max(st.session_state['stockData']['Adj Close'].values)+0.5])).title('')
            ),
        use_container_width=True)
    