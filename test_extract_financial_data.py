# External modules:
import unittest
import pandas
import datetime

# Internal modules:
from extract_financial_data import FinancialAssetList, FinancialData


class TestFinancialAssetList(unittest.TestCase):

    def setUp(self):
        self.financial_asset_list_object = FinancialAssetList()
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

    def test_financial_asset_list_tickers(self):
        tickers = self.financial_asset_list_object.tickers
        self.assertIsNotNone(tickers)
        self.assertIn(self.ticker1, tickers)
        self.assertIn(self.ticker2, tickers)
        self.assertIn(self.ticker3, tickers)

    def test_financial_asset_list_readable_stock_list(self):
        readable_stock_list = self.financial_asset_list_object.readable_stock_list
        self.assertIsNotNone(readable_stock_list)
        self.assertIn(self.readable_stock1, readable_stock_list)
        self.assertIn(self.readable_stock2, readable_stock_list)
        self.assertIn(self.readable_stock3, readable_stock_list)

    def test_financial_asset_list_get_stock_info(self):
        stock_info = self.financial_asset_list_object.get_stock_info(self.ticker1)
        self.assertIsInstance(stock_info, dict)
        self.assertEqual(stock_info['symbol'], self.ticker1)
        self.assertEqual(stock_info['country'], self.country1)

    def test_financial_asset_list_get_stock_info_to_string(self):
        stock_info_string = self.financial_asset_list_object.get_stock_info_to_string(self.ticker3)
        self.assertIsInstance(stock_info_string, str)
        self.assertIn(self.name1, stock_info_string)

    def test_financial_asset_list_get_ticker_from_readable_stock(self):
        self.assertEqual(self.financial_asset_list_object.get_ticker_from_readable_stock(self.readable_stock1),
                         self.ticker1)
        self.assertEqual(self.financial_asset_list_object.get_ticker_from_readable_stock(self.readable_stock2),
                         self.ticker2)


class TestFinancialDate(unittest.TestCase):

    def setUp(self):
        self.ticker1 = 'AAPL' # Apple
        self.ticker2 = 'MSFT'  # Microsoft
        self.financial_data_object1 = FinancialData(self.ticker1)
        self.financial_data_object2 = FinancialData(self.ticker2)
        self.start_date1 = '2010-01-01'
        self.end_date1 = datetime.date.today()
        self.trade_day1 = '2010-01-04'

    def tearDown(self):
        pass

    def test_financial_data_get_stock_df_by_period(self):
        apple_ytd = self.financial_data_object1.get_stock_df_by_period()
        microsoft_1day = self.financial_data_object2.get_stock_df_by_period(period='1d')
        microsoft_max = self.financial_data_object2.get_stock_df_by_period(period='max')
        self.assertIsInstance(apple_ytd, pandas.core.frame.DataFrame)
        self.assertIsInstance(microsoft_1day, pandas.core.frame.DataFrame)
        self.assertIsInstance(microsoft_max, pandas.core.frame.DataFrame)
        self.assertIsNotNone(microsoft_max.iloc[1].Open)
        self.assertIsNotNone(microsoft_max.iloc[1].High)
        self.assertIsNotNone(microsoft_max.iloc[1].Low)
        self.assertIsNotNone(microsoft_max.iloc[1].Close)
        self.assertIsNotNone(microsoft_max.iloc[1].Volume)

    def test_financial_data_get_stock_df_by_dates(self):
        apple_date1 = self.financial_data_object1.get_stock_df_by_dates(self.start_date1, self.end_date1)
        self.assertIsInstance(apple_date1, pandas.core.frame.DataFrame)
        self.assertIsInstance(apple_date1.index, pandas.core.indexes.datetimes.DatetimeIndex)
        self.assertIsNotNone(apple_date1.loc[self.trade_day1].Open)
        self.assertIsNotNone(apple_date1.loc[self.trade_day1].High)
        self.assertIsNotNone(apple_date1.loc[self.trade_day1].Low)
        self.assertIsNotNone(apple_date1.loc[self.trade_day1].Close)
        self.assertIsNotNone(apple_date1.loc[self.trade_day1].Volume)











