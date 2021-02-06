import unittest
import pandas
from extract_financial_data import FinancialData
import datetime


class TestFinancialData(unittest.TestCase):

    def setUp(self):
        self.financial_data_object = FinancialData()
        self.ticker1 = 'AAPL'  # Apple
        self.ticker2 = 'MSFT'  # Microsoft
        self.ticker3 = 'AMZN'  # Amazon
        self.readable_stock1 = 'Apple Inc.---AAPL'
        self.readable_stock2 = 'Microsoft Corp.---MSFT'
        self.readable_stock3 = 'Amazon.com Inc.---AMZN'
        self.name1 = 'Amazon.com, Inc.'
        self.country1 = 'United States'
        self.start_date1 = '2010-01-01'
        self.end_date1 = datetime.date.today()
        self.trade_day1 = '2010-01-04'

    def tearDown(self):
        pass

    def test_financial_data_tickers(self):
        tickers = self.financial_data_object.tickers
        self.assertIsNotNone(tickers)
        self.assertIn(self.ticker1, tickers)
        self.assertIn(self.ticker2, tickers)
        self.assertIn(self.ticker3, tickers)

    def test_financial_data_readable_stock_list(self):
        readable_stock_list = self.financial_data_object.readable_stock_list
        self.assertIsNotNone(readable_stock_list)
        self.assertIn(self.readable_stock1, readable_stock_list)
        self.assertIn(self.readable_stock2, readable_stock_list)
        self.assertIn(self.readable_stock3, readable_stock_list)

    def test_financial_data_get_stock_info(self):
        stock_info = self.financial_data_object.get_stock_info(self.ticker1)
        self.assertIsInstance(stock_info, dict)
        self.assertEqual(stock_info['symbol'], self.ticker1)
        self.assertEqual(stock_info['country'], self.country1)

    def test_financial_data_get_stock_info_to_string(self):
        stock_info_string = self.financial_data_object.get_stock_info_to_string(self.ticker3)
        self.assertIsInstance(stock_info_string, str)
        self.assertIn(self.name1, stock_info_string)

    def test_financial_data_get_stock_history_based_on_period(self):
        stock_ytd = self.financial_data_object.get_stock_history_based_on_period(self.ticker2)
        stock_1day = self.financial_data_object.get_stock_history_based_on_period(self.ticker2, period='1d')
        stock_max = self.financial_data_object.get_stock_history_based_on_period(self.ticker2, period='max')
        self.assertIsInstance(stock_ytd, pandas.core.frame.DataFrame)
        self.assertIsInstance(stock_1day, pandas.core.frame.DataFrame)
        self.assertIsInstance(stock_max, pandas.core.frame.DataFrame)
        self.assertIsNotNone(stock_max.iloc[1].Open)
        self.assertIsNotNone(stock_max.iloc[1].High)
        self.assertIsNotNone(stock_max.iloc[1].Low)
        self.assertIsNotNone(stock_max.iloc[1].Close)
        self.assertIsNotNone(stock_max.iloc[1].Volume)

    def test_financial_data_get_stock_history_based_on_dates(self):
        apple_date1 = self.financial_data_object.get_stock_history_based_on_dates(self.ticker1, self.start_date1, self.end_date1)
        self.assertIsInstance(apple_date1, pandas.core.frame.DataFrame)
        self.assertIsInstance(apple_date1.index, pandas.core.indexes.datetimes.DatetimeIndex)
        self.assertIsNotNone(apple_date1.loc[self.trade_day1].Open)
        self.assertIsNotNone(apple_date1.loc[self.trade_day1].High)
        self.assertIsNotNone(apple_date1.loc[self.trade_day1].Low)
        self.assertIsNotNone(apple_date1.loc[self.trade_day1].Close)
        self.assertIsNotNone(apple_date1.loc[self.trade_day1].Volume)

    def test_financial_data_get_ticker_from_readable_stock(self):
        self.assertEqual(self.financial_data_object.get_ticker_from_readable_stock(self.readable_stock1), self.ticker1)
        self.assertEqual(self.financial_data_object.get_ticker_from_readable_stock(self.readable_stock2), self.ticker2)









