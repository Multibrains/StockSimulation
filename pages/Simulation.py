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

#########################
# Switch Page If Needed #
#########################

if 'gameStatus' not in st.session_state:
    switch_page('Initialization')

if st.session_state['gameStatus'] == True and st.session_state['simulationPeriod'] == st.session_state['len']:
     switch_page('Achivement')

####################
# Define Functions #
####################

def getSummaryValues(df,period,frequency,record):
    volume = round(sum(record[record.action == 'Buy'].volume) - sum(record[record.action == 'Sell'].volume),5)
    if len(record) == 0:
         balance = st.session_state['initMoney']
    else:
        balance = record['balance'][len(record)-1]
    if frequency == 'Daily':
        price = round(df['Adj Close'][period],5)
        todayDate = df['Date'][period]
    else:
        df_weekAgg = df.groupby(['week_accumulated']).agg({'Date': 'last', 'Adj Close': 'last'}).reset_index()
        price = df_weekAgg['Adj Close'][period]
        todayDate = df_weekAgg['Date'][period]
    totalAsset = round(price * volume,5)
    netProfit = round(totalAsset + balance - st.session_state['initMoney'],5)
    return price, volume, totalAsset, balance,netProfit, todayDate

#####################################
# Initialize Data and Session State #
#####################################

if 'tradeRecord' not in st.session_state and st.session_state['simulationPeriod'] == 0:
    st.session_state['tradeRecord'] = pd.DataFrame(columns=[
         'period', 'currentPrice', 'volume','action','totalAsset', 'balance', 'netProfit'
         ])

stockPrice, stockVolume, totalAsset, balance, netProfit,todayDate = getSummaryValues(
                          st.session_state['stockData'],
                          st.session_state['simulationPeriod'],
                          st.session_state['freq'],
                          st.session_state['tradeRecord'])

if len(st.session_state['tradeRecord']) == 0:
    st.session_state['tradeRecord'] = pd.concat([
        st.session_state['tradeRecord'],
        pd.DataFrame({
            'period': [st.session_state['simulationPeriod']], 
            'currentPrice': [stockPrice], 
            'volume': [stockVolume],
            'action': [''],
            'totalAsset': [0], 
            'balance': [balance], 
            'netProfit': [netProfit]
            })
            ])
    
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
    switch_page('app')
    
st.markdown("""
            <h1 style='text-align: center; color: Black;'>
                """ + st.session_state['stock'] +  
                """   --   """ + str(st.session_state['stockData']['Date'][st.session_state['simulationPeriod']]) + """
            </h1>
            """, unsafe_allow_html=True)

st.divider()

col1, col2, col3, col4, col5 = st.columns(5)

lenTradeRecord = len(st.session_state['tradeRecord'])

col1.metric(label="Today's Stock Price", value=round(stockPrice,2), delta=round(stockPrice-st.session_state['tradeRecord']['currentPrice'][max(0,lenTradeRecord-2)],2))
col2.metric(label="Volume Holding", value=round(stockVolume,2), delta=round(stockVolume-st.session_state['tradeRecord']['volume'][max(0,lenTradeRecord-2)],2))
col3.metric(label="Total Asset", value=round(totalAsset,2), delta=round(totalAsset-st.session_state['tradeRecord']['totalAsset'][max(0,lenTradeRecord-2)],2))
col4.metric(label="Balance", value=round(balance,2), delta=round(balance-st.session_state['tradeRecord']['balance'][max(0,lenTradeRecord-2)],2))
col5.metric(label="Net Profit", value=round(netProfit,2), delta=round(netProfit-st.session_state['tradeRecord']['netProfit'][max(0,lenTradeRecord-2)],2))

style_metric_cards()

tab1, tab2, tab3 = st.tabs(["📈1 Month", "📈1 Year", "📈Max"])
with tab1:

    availableData_month = pd.concat([
         st.session_state['oneMonthHistory_data'],
         st.session_state['stockData'][:st.session_state['simulationPeriod']+1]
    ])

    st.altair_chart(
            alt.Chart(availableData_month).mark_line().encode(
            alt.X('Date', axis=alt.Axis(labelAngle=-30)).title(''),
            alt.Y('Adj Close',scale=alt.Scale(domain=[
                min(availableData_month['Adj Close'].values)-0.5,
                max(availableData_month['Adj Close'].values)+0.5])).title('')
                )+
            alt.Chart(availableData_month).mark_circle(size=100).encode(
            alt.X('Date', axis=alt.Axis(labelAngle=-30)).title(''),
            alt.Y('Adj Close',scale=alt.Scale(domain=[
                min(availableData_month['Adj Close'].values)-0.5,
                max(availableData_month['Adj Close'].values)+0.5])).title('')
                ),
            use_container_width=True)
    
with tab2:

    availableData_year = pd.concat([
         st.session_state['oneYearHistory_data'],
         st.session_state['stockData'][:st.session_state['simulationPeriod']+1]
    ])

    st.altair_chart(
            alt.Chart(availableData_year).mark_line().encode(
            alt.X('Date', axis=alt.Axis(labelAngle=-30)).title(''),
            alt.Y('Adj Close',scale=alt.Scale(domain=[
                min(availableData_year['Adj Close'].values)-0.5,
                max(availableData_year['Adj Close'].values)+0.5])).title('')
                )+
            alt.Chart(availableData_year).mark_circle(size=100).encode(
            alt.X('Date', axis=alt.Axis(labelAngle=-30)).title(''),
            alt.Y('Adj Close',scale=alt.Scale(domain=[
                min(availableData_year['Adj Close'].values)-0.5,
                max(availableData_year['Adj Close'].values)+0.5])).title('')
                ),
            use_container_width=True)
    

with tab3:

    availableData_max = pd.concat([
         st.session_state['maxHistory_data'],
         st.session_state['stockData'][:st.session_state['simulationPeriod']+1]
    ])

    st.altair_chart(
            alt.Chart(availableData_max).mark_line().encode(
            alt.X('Date', axis=alt.Axis(labelAngle=-30)).title(''),
            alt.Y('Adj Close',scale=alt.Scale(domain=[
                min(availableData_max['Adj Close'].values)-0.5,
                max(availableData_max['Adj Close'].values)+0.5])).title('')
                )+
            alt.Chart(availableData_max).mark_circle(size=100).encode(
            alt.X('Date', axis=alt.Axis(labelAngle=-30)).title(''),
            alt.Y('Adj Close',scale=alt.Scale(domain=[
                min(availableData_max['Adj Close'].values)-0.5,
                max(availableData_max['Adj Close'].values)+0.5])).title('')
                ),
            use_container_width=True)
    
inputCol1, inputCol2, inputCol3 = st.columns([2,3,2])

with inputCol2:
    if st.session_state['simulationPeriod'] == st.session_state['len']-1:
        tradeAction = st.selectbox('Trade Action',['Sell'], label_visibility='collapsed')
        tradeAmount = st.number_input(label="Amount you want to trade",
                                    min_value=totalAsset,max_value=totalAsset,step=0.01)
    else:
        tradeAction = st.selectbox('Trade Action',('Buy', 'Sell'), label_visibility='collapsed')
        if tradeAction == 'Buy':
            maxTradeAmount = balance
        else:
            maxTradeAmount = round(stockVolume*stockPrice,2)
        tradeAmount = st.number_input(label="Amount you want to trade",
                                    min_value=0.00,max_value=maxTradeAmount,step=0.01)
    
    st.divider()

    subCol1,subCol2,subCol3 = st.columns([0.5,1,1])
    with subCol2:
        with stylable_container(
                        key="trade_button",
                        css_styles="""
                            button {
                                background-color: green;
                                color: white;
                                border-radius: 30px;
                                height: 55px;
                                width: 300px;
                            }
                            """,
                    ):
                    submit = st.button('Confirm '+tradeAction+'ing '+str(round(tradeAmount/stockPrice,2))+' shares',key='trade_button')

        if totalAsset != 0 and st.session_state['simulationPeriod'] == st.session_state['len']-1:
            with stylable_container(
                            key="next_day_button",
                            css_styles="""
                                button {
                                    background-color: LightSlateGray;
                                    color: white;
                                    border-radius: 30px;
                                    height: 55px;
                                    width: 300px;
                                }
                                """,
                        ):
                        nextday = st.button('Process to next day',key='next_day_button',disabled=True)
        else:
            with stylable_container(
                            key="next_day_button",
                            css_styles="""
                                button {
                                    background-color: LightSlateGray;
                                    color: white;
                                    border-radius: 30px;
                                    height: 55px;
                                    width: 300px;
                                }
                                """,
                        ):
                        nextday = st.button('Process to next day',key='next_day_button')

if submit:
    if tradeAction == 'Buy':
        balance = st.session_state['tradeRecord']['balance'][lenTradeRecord-1] - tradeAmount
    else:
        balance = st.session_state['tradeRecord']['balance'][lenTradeRecord-1] + tradeAmount
    st.session_state['tradeRecord'] = pd.concat([
        st.session_state['tradeRecord'],
        pd.DataFrame({
             'period': [st.session_state['simulationPeriod']], 
             'currentPrice': [stockPrice], 
             'volume': [round(tradeAmount/stockPrice,5)],
             'action': [tradeAction],
             'totalAsset': [totalAsset], 
             'balance': [balance], 
             'netProfit': [netProfit]})
    ]).reset_index().drop(['index'],axis=1)
    st.rerun()

if nextday:
    if st.session_state['simulationPeriod'] not in st.session_state['tradeRecord']['period'].unique():
        st.session_state['tradeRecord'] = pd.concat([
            st.session_state['tradeRecord'],
            pd.DataFrame({
                'period': [st.session_state['simulationPeriod']], 
                'currentPrice': [stockPrice], 
                'volume': [st.session_state['tradeRecord']['volume'][lenTradeRecord-1]],
                'action': [''],
                'totalAsset': [totalAsset], 
                'balance': [balance], 
                'netProfit': [netProfit]})
        ]).reset_index().drop(['index'],axis=1)
    st.session_state['simulationPeriod'] += 1
    st.rerun()
