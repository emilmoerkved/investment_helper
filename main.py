from extract_financial_data import FinancialData
import gui

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def main():
    financial_data = FinancialData()
    gui.create_gui(financial_data)


if __name__ == '__main__':
    main()

