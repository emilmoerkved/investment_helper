from extract_financial_data import FinancialData
from gui import *
import test_extract_financial_data
import test_technical_analysis
import unittest


def main():
    # exit=False to run the rest of the code
    #unittest.main(module=test_extract_financial_data, exit=False)
    #unittest.main(module=test_technical_analysis, exit=True)
    financial_data = FinancialData()
    Gui(financial_data).start()


if __name__ == '__main__':
    main()

