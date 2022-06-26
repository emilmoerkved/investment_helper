import csv
import pandas as pd
import yfinance as yf
import datetime
import pandas_market_calendars as mcal


class FinancialData:

    def __init__(self):
        self.asset_dictionary = {}
        self.readable_stock_list = []
        self.companylist = []
        self.tickers = []
        self.market = 'S&P 500'
        self.country = 'USA'
        self._fill_sp500()

    def change_marketlist(self, market='S&P 500', country='USA'):
        print(market, country)
        self._clear_list()
        if market == 'S&P 500' and country == 'USA':
            self._fill_sp500()
        elif market == 'Oslo Stock Exchange' and country == 'NOR':
            self._fill_obx()
        elif market == 'Nasdaq Stockholm' and country == 'SWE':
            self._fill_nasdaq_stockholm()
        elif market == 'Railway' and country == 'WORLD':
            self._fill_railway_shares()
        elif market == 'Indexes and Other' and country == 'WORLD':
            self._fill_indexes_and_other()
        self.market = market
        self.country = country

    def _clear_list(self):
        self.asset_dictionary.clear()
        self.readable_stock_list = []
        self.tickers = []
        self.companylist = []

    def _fill_sp500(self):
        df = self._get_sp500()  # ['Symbol', 'Security']
        for i in range(len(df)):
            self.tickers.append(df['Symbol'][i])
            self.companylist.append(df['Security'][i])
            self.asset_dictionary[df['Security'][i]] = df['Symbol'][i]
            self.readable_stock_list.append('---'.join([df['Security'][i], df['Symbol'][i]]))

    def _get_sp500(self):
        table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        df = table[0]
        df.reset_index()
        return df[['Symbol', 'Security']]

    def _fill_obx(self):
        df = self._get_obx()
        for i in range(len(df)):
            ticker = df['Ticker'][i].split()[1]+'.OL'
            self.tickers.append(ticker)
            self.companylist.append(df['Company'][i])
            self.asset_dictionary[df['Company'][i]] = ticker
            self.readable_stock_list.append('---'.join([df['Company'][i], ticker]))

    def _get_obx(self):
        table = pd.read_html('https://en.wikipedia.org/wiki/List_of_companies_listed_on_the_Oslo_Stock_Exchange')
        df = table[1]
        df.reset_index()
        print(df.head)
        return df[['Company', 'Ticker']]

    def _fill_nasdaq_stockholm(self):
        df = self._get_nasdaq_stockholm()
        for i in range(len(df)):
            print(i)
            print(df['Ticker'][i])
            ticker = df['Ticker'][i]+'.ST'
            print(ticker)
            self.tickers.append(ticker)
            self.companylist.append(str(df['Company'][i]))
            self.asset_dictionary[str(df['Company'][i])] = ticker
            print(df['Company'][i])
            self.readable_stock_list.append('---'.join([str(df['Company'][i]), ticker]))

    def _get_nasdaq_stockholm(self):
        df = pd.read_csv('NasdaqStockholmShares.txt', delimiter=';', encoding='utf-8')
        df.reset_index()
        print(df.columns)
        return df[['Company', 'Ticker']]

    def get_yield_curve(self, period='ytd'):
        if period == 'ytd':
            year = str(datetime.datetime.now().year)
        table = pd.read_html('https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yieldYear&year='+year)
        df = table[1]
        df['Datetime'] = pd.to_datetime(df['Date'], format='%m/%d/%y')
        df.drop(['Date'], axis='columns', inplace=True)
        df.set_index(['Datetime'], inplace=True)
        return df

    def _fill_railway_shares(self):
        df = self._get_railway_shares()
        for i in range(len(df)):
            if df['StockExchange'][i] == 'NYSE':
                ticker = str(df['Ticker'])
            self.tickers.append(ticker)
            company = str(df['Company'][i])
            self.companylist.append(company)
            self.asset_dictionary[company] = ticker
            print(company)
            print(ticker)
            self.readable_stock_list.append('---'.join([company, ticker]))

    def _get_railway_shares(self):
        df = pd.read_csv('RailwayShares.txt', delimiter=';', encoding='utf-8')
        df.reset_index()
        print(df.columns)
        return df[['Company', 'Ticker', 'StockExchange']]

    def _fill_indexes_and_other(self):
        df = self._get_indexes_and_other()
        for i in range(len(df)):
            ticker = df['Ticker'][i]
            self.tickers.append(ticker)
            self.companylist.append(df['Company'][i])
            self.asset_dictionary[df['Company'][i]] = ticker
            self.readable_stock_list.append('---'.join([df['Company'][i], ticker]))

    def _get_indexes_and_other(self):
        data = [['S&P 500', '^GSPC'],
                ['Nasdaq Composite', '^IXIC'],
                ['13 Week Treasury Bill', '^IRX'],
                ['Treasury Yield 5 Years', '^FVX'],
                ['Treasury Yield 10 Years', '^TNX'],
                ['Treasury Yield 30 Years', '^TYX'],
                ['Yield Curve', 'SPECIAL: YIELD_CURVE'],
                ['Gold', 'GC=F'],
                ['Bitcoin', 'BTC-USD']]
        df = pd.DataFrame(data, columns=['Company', 'Ticker'])
        return df

    def get_stock_info(self, ticker):
        stock_ticker = yf.Ticker(ticker)
        stock_info = stock_ticker.info
        return stock_info

    def get_stock_financials(self, ticker):
        stock_ticker = yf.Ticker(ticker)
        stock_financials = stock_ticker.financials
        return stock_financials

    def get_stock_balance_sheet(self, ticker):
        stock_ticker = yf.Ticker(ticker)
        stock_balance_sheet = stock_ticker.balancesheet
        return stock_balance_sheet

    def get_stock_cashflow(self, ticker):
        stock_ticker = yf.Ticker(ticker)
        stock_cashflow = stock_ticker.cashflow
        return stock_cashflow

    def get_stock_dividends(self, ticker):
        stock_ticker = yf.Ticker(ticker)
        stock_dividens = stock_ticker.dividends
        return stock_dividens

    def get_stock_shareholders(self, ticker):
        stock_ticker = yf.Ticker(ticker)
        stock_shareholders = stock_ticker.major_holders
        return stock_shareholders

    def get_stock_earnings(self, ticker):
        stock_ticker = yf.Ticker(ticker)
        stock_earnings = stock_ticker.earnings
        return stock_earnings

    def get_stock_info_to_string(self, ticker, stock_info_dict):
        string = '----- ' + ticker + ' -----\n'
        string += 'NAME: ' + stock_info_dict['longName'] + '\n'
        string += 'SECTOR: ' + stock_info_dict['sector'] + '\n'
        string += 'BUSINESS SUMMARY: ' + stock_info_dict['longBusinessSummary']
        return string

    def get_name_from_ticker(self, ticker):
        return yf.Ticker(ticker).info['shortName']

    def get_news(self, ticker):
        return yf.Ticker(ticker).news

    def get_recommendations(self, ticker):
        return yf.Ticker(ticker).recommendations

    def get_stock_history_based_on_period(self, ticker, period='ytd'):
        if period == '1d':
            granularity = '1m'
        else:
            granularity = '1d'
        df = yf.download(tickers=ticker, period=period, interval=granularity, auto_adjust=True, threads=False)
        return df[['Open', 'High', 'Low', 'Close', 'Volume']]

    def get_stock_history_based_on_dates(self, ticker, startdate, enddate):
        df = yf.download(tickers=ticker, start=startdate, end=enddate, auto_adjust=True)
        return df[['Open', 'High', 'Low', 'Close', 'Volume']]

    def get_ticker_from_readable_stock(self, readable_stock):
        ticker = readable_stock[readable_stock.index('---')+3:]
        return ticker

    def get_yfinance_periods(self):
        return {'year to date': 'ytd', '1 day': '1d', '5 days': '5d', '1 month': '1mo', '3 months': '3mo',
                '6 months': '6mo', '1 year': '1y', '2 years': '2y', '5 years': '5y', '10 years': '10y', 'max': 'max'}

    def get_yfinance_period_value(self, key):
        period_dict = {'year to date': 'ytd', '1 day': '1d', '5 days': '5d', '1 month': '1mo', '3 months': '3mo',
                       '6 months': '6mo', '1 year': '1y', '2 years': '2y', '5 years': '5y', '10 years': '10y',
                       'max': 'max'}
        return period_dict[key]


# period can be 1m, 3m, 6m, 1y, 2y, 5y, 10y, ytd
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



