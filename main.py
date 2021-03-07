# External modules:
import unittest

# Internal modules:
from gui import *
import test_extract_financial_data
import test_technical_analysis

from extract_financial_data import FinancialData, FinancialAssetList

def main():
    # exit=False to run the rest of the code
    #unittest.main(module=test_extract_financial_data, exit=False)
    #unittest.main(module=test_technical_analysis, exit=True)
    # financial_asset_list_object = FinancialAssetList()
    # print(financial_asset_list_object.get_obx())
    # financial_obj = FinancialData('AKER.Ok')
    # df = financial_obj.get_stock_df_by_period()
    # # print(df.head)
    Gui().start()


if __name__ == '__main__':
    main()

