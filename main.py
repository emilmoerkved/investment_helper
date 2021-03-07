# External modules:
import unittest

# Internal modules:
from gui import *
import test_extract_financial_data
import test_technical_analysis



def main():
    # exit=False to run the rest of the code
    #unittest.main(module=test_extract_financial_data, exit=False)
    #unittest.main(module=test_technical_analysis, exit=True)
    Gui().start()


if __name__ == '__main__':
    main()

