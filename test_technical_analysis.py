import datetime
import unittest
from technical_analysis import TechnicalAnalysis
from extract_financial_data import FinancialData

class TestTechnicalAnalysis(unittest.TestCase):

    def setUp(self):
        self.ticker = 'AMZN'
        self.financial_data_object = FinancialData()
        self.start_date = '2010-01-01'
        self.end_date = '2012-01-01'
        self.last_trade_day = datetime.date(2011, 12, 30)
        self.yf_df = self.financial_data_object.get_stock_history_based_on_dates(self.ticker, self.start_date, self.end_date)
        self.technical_analysis_object = TechnicalAnalysis(self.ticker)


    def tearDown(self):
        pass

    def test_find_resistance_levels(self):
        self.technical_analysis_object.find_resistance_levels(self.yf_df)
        self.assertIsNotNone(self.technical_analysis_object.resistance)
        self.assertEqual(self.technical_analysis_object.resistance_update_date, self.last_trade_day)

    def test_find_support_levels(self):
        self.technical_analysis_object.find_support_levels(self.yf_df)
        self.assertIsNotNone(self.technical_analysis_object.support)
        self.assertEqual(self.technical_analysis_object.support_update_date, self.last_trade_day)