
import pandas as pd
import yfinance as yf

tickers = pd.read_csv('CNDX_holdings.csv', skiprows=2).dropna()
tickers = tickers['Ticker']

precios = {}
for i in tickers:
    pr = yf.download(i, start='2015-01-01', end='2021-02-08', interval='1d')
    pr = pr.reset_index()
    precios[i] = pr