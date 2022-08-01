# -*- coding: utf-8 -*-
"""
Created on Sat Jul 30 16:38:17 2022

@author: bruce
"""

# libraries

import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy_financial as npf
from io import BytesIO
from datetime import date
import numpy as np



# relevant urls
# C:\Users\bruce\portfolio_app
# https://raw.githubusercontent.com/YellowSkin22/portfolio_app/main/holdings.csv?token=GHSAT0AAAAAABXEPX2VSVW3YNXRRRTHAGWAYXFJGFA
# https://raw.githubusercontent.com/YellowSkin22/portfolio_app/main/other_transactions.csv
# https://raw.githubusercontent.com/YellowSkin22/portfolio_app/main/transactions.csv



### --- functions --- ###

def last_quote(ticker):
    if ticker == 'CASH':
        last_quote = 1
    else:
        last_quote = yf.Ticker(ticker).history()['Close'].iloc[-1]
        
    return last_quote


### --- Visualization Functions --- ### 


### --- DataFrame work --- ###

holdings_url = 'https://raw.githubusercontent.com/YellowSkin22/portfolio_app/main/holdings.csv?token=GHSAT0AAAAAABXEPX2VSVW3YNXRRRTHAGWAYXFJGFA' # <- set url for holdings
holdings_df = pd.read_csv(holdings_url) # <- turn csv into dataframe
holdings_df['last_quote'] = holdings_df.apply(lambda row: last_quote(row['ticker']), axis=1) # <- get last quote by using function
holdings_df['total'] = holdings_df.holdings * holdings_df.last_quote # <- calculating the total value of the holding

transactions_url = 'https://raw.githubusercontent.com/YellowSkin22/portfolio_app/main/transactions.csv'
transactions_df = pd.read_csv(transactions_url)
transactions_df.dropna(how='all',
                       axis=1,
                       inplace=True)

other_transactions_url = 'https://raw.githubusercontent.com/YellowSkin22/portfolio_app/main/other_transactions.csv'
other_transactions_df = pd.read_csv(other_transactions_url)


## --- Prepare sub Data Frames --- ##

holdings_total = holdings_df.total.sum()

securities_df = holdings_df[holdings_df['type'] == 'security']
securities_total = securities_df.total.sum()

crypto_df = holdings_df[holdings_df['type'] == 'crypto'] 
crypto_total = crypto_df.total.sum()

cash_df = holdings_df[holdings_df['type'] == 'cash']
cash_total = cash_df.total.sum()

summary_df = holdings_df.groupby(['type'], as_index=False).sum()

dividends_df = other_transactions_df[other_transactions_df['description'] == 'dividend']
dividends_total = dividends_df.amount.sum()


## - Mortgage DataFrame - ##


# https://pbpython.com/amortization-model.html

principal = 314700
interest_rate = 0.0197 / 12

principal_2 = 3300
interest_rate_2 = 0.0164 / 12

periods = 30 * 12
start_date = (date(year=2019,
                   month=2,
                   day=1))

pmt = npf.pmt(interest_rate, periods, principal)

# - Prepare Mortgage DataFrame - #
periods_list = list()
for x in range(0,360): #<- number of months in my mortgage plan
    periods_list.append(x)


# - Get Date Range for DataFrame - #
rng = pd.date_range(start_date,
                    periods=periods,
                    freq='MS')

rng.name = 'payment_date'

mortgage_data = {'period':periods_list,
                 'payment_date':rng}

mortgage_df = pd.DataFrame(mortgage_data)


# - first mortgage part - #
mortgage_df['payment_a'] = npf.pmt(interest_rate, periods, principal)
mortgage_df['interest_a'] = npf.ipmt(interest_rate, mortgage_df.period, periods, principal)
mortgage_df['principal_a'] = npf.ppmt(interest_rate, mortgage_df.period, periods, principal)
mortgage_df['cumulative_principal_a'] = mortgage_df.principal_a.cumsum()
mortgage_df['current_balance_a'] = principal + mortgage_df.cumulative_principal_a

# - second mortgage part - #
mortgage_df['payment_b'] = npf.pmt(interest_rate_2, periods, principal_2)
mortgage_df['interest_b'] = npf.ipmt(interest_rate_2, mortgage_df.period, periods, principal_2)
mortgage_df['principal_b'] = npf.ppmt(interest_rate_2, mortgage_df.period, periods, principal_2)
mortgage_df['cumulative_principal_b'] = mortgage_df.principal_b.cumsum()
mortgage_df['current_balance_b'] = principal_2 + mortgage_df.cumulative_principal_b

# - all mortgage parts - #
mortgage_df['payment_total'] = mortgage_df.payment_a + mortgage_df.payment_b
mortgage_df['interest_total'] = mortgage_df.interest_a + mortgage_df.interest_b
mortgage_df['principal_total'] = mortgage_df.principal_a + mortgage_df.principal_b
mortgage_df['cumulative_principal_total'] = mortgage_df.principal_total.cumsum()
mortgage_df['current_balance_total'] = principal + principal_2 + mortgage_df.cumulative_principal_total

#<- define current period
## -- Visualisations -- ## 

# - Font Sizes - #

SMALL_SIZE = 8
MEDIUM_SIZE = 12
BIGGER_SIZE = 14 

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

# -- Asset Type Pie Chart -- #

# Pie chart, where the slices will be ordered and plotted counter-clockwise:
labels = summary_df.type
sizes = summary_df.total

fig1, ax1 = plt.subplots(figsize=(4, 4))

ax1.pie(sizes,
        labels=labels,
        autopct='%1.1f%%', 
        startangle=90)

# draw circle
centre_circle = plt.Circle((0, 0), 0.70, fc='white')
fig1 = plt.gcf()
  
# Adding Circle in Pie chart
fig1.gca().add_artist(centre_circle)

buf = BytesIO()
fig1.savefig(buf, format="png")


# - Mortgage Chart - #
x = mortgage_df.payment_date
y1 = mortgage_df.current_balance_total
y2 = mortgage_df.current_balance_a
y3 = mortgage_df.current_balance_b

fig2, ax2 = plt.subplots()  # Create a figure containing a single axes.
ax2.plot(x, y1);  # Plot some data on the axes.

### --- Streamlit App --- ### 

## -- Display -- ## 
st. set_page_config(layout="wide")



## -- Test Area -- ##

# st.write(holdings_df)
# st.write(transactions_df)

## -- Content -- ## 

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(label='Securities',
              value='{:,}'.format(round(securities_total,2)),
              delta=None)
    
with col2:
    st.metric(label='Crypto Currency',
              value='{:,}'.format(round(crypto_total,2)),
              delta=None)
    
with col3:
    st.metric(label='Cash',
              value='{:,}'.format(round(cash_total,2)),
              delta=None)
    
with col4:
    st.metric(label='Realized gains',
              value='tbd',
              delta=None)
    
with col5:
    st.metric(label='Dividends',
              value='{:,}'.format(round(dividends_total,2)),
              delta=None)
    
with col6:
    st.metric(label='Portfolio',
              value='{:,}'.format(round(holdings_total,2)),
              delta=None)


tab1, tab2, tab3 = st.tabs(["Asset Diversification", "Mortgage Breakdown", "Owl"])

with tab1:
    st.header('Asset Type Diversification')
    
    col1, col2 = st.columns((3,1))
    
    with col1:
        st.image(buf)
        

with tab2:
    st.header("Mortgage")
    # st.write(mortgage_df.current_balance)
    # st.write(pmt)
    st.write(mortgage_df)
    
    col1, col2 = st.columns((3,1))
    
    with col1:
        st.write('placeholder')
        st.pyplot(fig2)

with tab3:
    st.header("An owl")
    st.image("https://static.streamlit.io/examples/owl.jpg", width=200)
    