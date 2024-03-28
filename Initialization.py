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

############################
# Initialize Session State #
############################

if 'stock' not in st.session_state:
    st.session_state['stock'] = ''

if 'freq' not in st.session_state:
    st.session_state['freq'] = 0

if 'len' not in st.session_state:
    st.session_state['len'] = 0

if 'initMoney' not in st.session_state:
    st.session_state['initMoney'] = 0.0

if 'gameStatus' not in st.session_state:
    st.session_state['gameStatus'] = False

if 'simulationPeriod' not in st.session_state:
    st.session_state['simulationPeriod'] = 0

########################
# Initialize Functions #
########################

def getTicker(input):
    return input[input.index('(')+1:input.index(')')]

def getData(stock, period):
    data = yf.download(stock,period=period).reset_index()
    data['Date'] = pd.to_datetime(data['Date']).dt.strftime('%Y-%m-%d')
    return data

def getRandomData(df, frequency, length):
    if frequency == 'Daily':
        num_day = len(df)
        start_index = random.randrange(0,num_day-length)
        simulation_data = df[start_index:start_index+length].reset_index().drop(['index'],axis=1)
        maxHistory_data = df[:start_index].reset_index().drop(['index'],axis=1)
        oneMonthHistory_data = df[start_index-31:start_index].reset_index().drop(['index'],axis=1)
        oneYearHistory_data = df[start_index-366:start_index].reset_index().drop(['index'],axis=1)
        return simulation_data, maxHistory_data, oneMonthHistory_data, oneYearHistory_data
    else:
        df['year'] = pd.to_datetime(df['Date']).dt.year
        df['week'] = pd.to_datetime(df['Date']).dt.isocalendar().week
        df['week_accumulated'] = df[['year','week']].apply(tuple, axis=1).rank(method='dense').astype('int')
        df['week_accumulated'] = np.where(np.logical_and(df['week_accumulated']==1,pd.to_datetime(df['Date']).dt.month==12), df['week_accumulated']+52, df['week_accumulated'])
        max_week = max(df['week_accumulated'])
        min_week = min(df['week_accumulated'])
        start_index = random.randrange(min_week, max_week-length)
        simulation_data = df[
            np.logical_and(df.week_accumulated >= start_index, 
                           df.week_accumulated < start_index+length)].reset_index().drop(['index'],axis=1)
        maxHistory_data = df[df.week_accumulated < start_index].reset_index().drop(['index'],axis=1)
        oneMonthHistory_data = df[
            np.logical_and(df.week_accumulated >= start_index-31, 
                           df.week_accumulated < start_index)].reset_index().drop(['index'],axis=1)
        oneYearHistory_data =df[
            np.logical_and(df.week_accumulated >= start_index-366, 
                           df.week_accumulated < start_index)].reset_index().drop(['index'],axis=1)
        return simulation_data, maxHistory_data, oneMonthHistory_data, oneYearHistory_data

############################
# Initialize Page and Data #
############################

st.set_page_config(
    page_title="Stock Simulation Playground",
    layout="wide",
    initial_sidebar_state='collapsed'
)

stock_info = pd.read_csv('data/stock_info.csv')

#####################
# Main Page Content #
#####################

st.markdown("""
            <h1 style='text-align: center; color: Black;'>
                Stock Market Simulation
            </h1>
            """, unsafe_allow_html=True)

st.divider()

col1,col2,col3 = st.columns([5,2,5])

with col1:
    stock_select = st.selectbox(
    'Select the stock you want', 
    options=stock_info.output, index=None
    )
    initial_money = st.slider(
        'Start-up capital',
        min_value=0.00, max_value=10000.00, value=5000.00, step=100.00
        )
with col3:
    frequency = st.selectbox(
        'Frequency of trade',['Daily','Weekly']
        )
    if frequency == 'Daily':
        freq_str = 'days'
    else:
        freq_str = 'weeks'
    length = st.number_input(
        'Number of ' + freq_str + ' you want to play',
        min_value=1, step=1, value=3)

st.divider()

if stock_select != None:
    current_stock_dta = getData(getTicker(stock_select),'max')
    if len(current_stock_dta) > 0:
        st.altair_chart(
            alt.Chart(current_stock_dta).mark_line().encode(
            alt.X('Date', axis=alt.Axis(labelAngle=-30)).title(''),
            alt.Y('Adj Close',scale=alt.Scale(domain=[
                min(current_stock_dta['Adj Close'].values)-5,
                max(current_stock_dta['Adj Close'].values)+5])).title('')
        ), 
            use_container_width=True)
        subcol1,subcol2,subcol3 = st.columns([5,2,5])
        with subcol2:
            with stylable_container(
                    key="start_button",
                    css_styles="""
                        button {
                            background-color: green;
                            color: white;
                            border-radius: 20px;
                            height: 50px;
                            width: 200px;
                        }
                        """,
                ):
                st.session_state['gameStatus'] = st.button('Start Simulation Now',key='start_button')
    else:
        st.error('Sorry, this stock is not available in the system. Please try another stock.', icon="🚨")

if st.session_state['gameStatus']:
    st.session_state['stock'] = stock_select
    st.session_state['freq'] = frequency
    st.session_state['len'] = length
    st.session_state['initMoney'] = initial_money
    st.session_state['stockData'], st.session_state['maxHistory_data'], st.session_state['oneMonthHistory_data'], st.session_state['oneYearHistory_data'] = getRandomData(current_stock_dta[['Date','Adj Close','Volume']],
                    st.session_state['freq'],
                    st.session_state['len']) 
    switch_page("Simulation")

