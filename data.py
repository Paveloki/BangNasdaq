import pandas as pd
import yfinance as yf
import datetime

now = datetime.datetime.now()
tickers = pd.read_csv('CNDX_holdings.csv', skiprows=2).dropna()
tickers = tickers['Ticker']

precios = {}
for i in tickers:
    pr = yf.download(i, start='2018-01-01', end=now, interval='1d')
    pr = pr.drop(['Adj Close'], axis=1)
    pr = pr.reset_index()
    precios[i] = pr

NASDAQ = yf.download('^IXIC', start='2018-01-01', end=now, interval='1d')
NASDAQ = NASDAQ.drop(['Adj Close'], axis=1)
NASDAQ = NASDAQ.reset_index()

rf = 0.015
