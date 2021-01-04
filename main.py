from extract_financial_data import FinancialData
import gui


def main():
    financial_data = FinancialData()
    gui.create_gui(financial_data)


if __name__ == '__main__':
    main()

