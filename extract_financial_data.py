import pandas as pd
import yfinance as yf
import datetime
import pandas_market_calendars as mcal

from technical_analysis import TechnicalAnalysis


class FinancialAssetList:

    def __init__(self):
        self.readable_stock_list = []
        self.tickers = []
        self.default_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
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

    def get_stock_info_to_string(self, ticker):
        stock_info_dict = self.get_stock_info(ticker)
        string = '----- ' + ticker + ' -----\n'
        string += 'NAME: ' + stock_info_dict['longName'] + '\n'
        string += 'SECTOR: ' + stock_info_dict['sector'] + '\n'
        string += 'BUSINESS SUMMARY: ' + stock_info_dict['longBusinessSummary']
        return string

    def get_ticker_from_readable_stock(self, readable_stock):
        ticker = readable_stock[readable_stock.index('---')+3:]
        return ticker


class FinancialData:

    def __init__(self, ticker):
        self.ticker = ticker
        self.technical_analysis = TechnicalAnalysis(self.ticker)

    def get_stock_df_by_period(self, period='ytd'):
        if period == '1d':
            granularity = '1m'
        else:
            granularity = '1d'
        df = yf.download(tickers=self.ticker, period=period, interval=granularity, auto_adjust=True)
        return df[['Open', 'High', 'Low', 'Close', 'Volume']]

    def get_stock_df_by_dates(self, startdate, enddate):
        df = yf.download(tickers=self.ticker, start=startdate, end=enddate, auto_adjust=True)
        return df[['Open', 'High', 'Low', 'Close', 'Volume']]


# period can be 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd
def get_date_from_period(period, mov_ave_days):
    date = datetime.date.today()
    if period == '1mo':
        date -= datetime.timedelta(days=30)
    elif period == '3mo':
        date -= datetime.timedelta(days=91)
    elif period == '6mo':
        date -= datetime.timedelta(days=182)
    elif period == '1y':
        date -= datetime.timedelta(days=365)
    elif period == '2y':
        date -= datetime.timedelta(days=730)
    elif period == '5y':
        date -= datetime.timedelta(days=1820)
    elif period == '10y':
        date -= datetime.timedelta(days=3650)
    elif period == 'ytd':
        date = datetime.date.fromisoformat('-'.join([str(date.year), '01', '01']))

    return get_startdate_of_mov_ave(date, mov_ave_days)


def get_startdate_of_mov_ave(date, days):
    nyse = mcal.get_calendar('NYSE')
    date_schedule = nyse.schedule(date-datetime.timedelta(days=days+days), date)
    t = date_schedule['market_open']
    market_days_array = []
    for market_date in t:
        dt = market_date.to_pydatetime().date()
        market_days_array.append(dt)
        if dt is date:
            break
    return market_days_array[-days]



