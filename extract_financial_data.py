import pandas as pd
import yfinance as yf


class FinancialData():

    def __init__(self):
        self.readable_stock_list = []
        self.tickers = []
        self._fill_stocks()

    def _fill_stocks(self):
        df = self._get_sp500()  # ['Symbol', 'Security']
        for i in range(len(df)):
            self.tickers.append(df['Symbol'][i])
            self.readable_stock_list.append('---'.join([df['Security'][i], df['Symbol'][i]]))

    def _get_sp500(self):
        table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        df = table[0]
        df.reset_index()
        return df[['Symbol', 'Security']]

    def get_stock_info(self, ticker):
        stock_ticker = yf.Ticker(ticker)
        stock_info = stock_ticker.info
        return stock_info

    def get_stock_info_to_string(self, ticker, stock_info_dict):
        string = '----- ' + ticker + ' -----\n'
        string += 'NAME: ' + stock_info_dict['longName'] + '\n'
        string += 'SECTOR: ' + stock_info_dict['sector'] + '\n'
        string += 'BUSINESS SUMMARY: ' + stock_info_dict['longBusinessSummary']
        return string

    def get_stock_history(self, ticker, period='ytd'):
        if period == '1d':
            granularity = '1m'
        else:
            granularity = '1d'
        df = yf.download(tickers=ticker, period=period, interval=granularity, auto_adjust=True)
        return df[['Open', 'High', 'Low', 'Close', 'Volume']]

    def get_ticker_from_readable_stock(self, readable_stock):
        ticker = readable_stock[readable_stock.index('---')+3:]
        return ticker
