class UserInput:

    def __init__(self):
        self.values = None
        self.event = None

    def set_event(self, event):
        self.event = event

    def set_values(self, values):
        self.values = values

    def get_ticker(self):
        if self.values['-STOCK-']:
            return self.values['-STOCK-'][0][self.values['-STOCK-'][0].index('---') + 3:]
        else:
            return ''

    def get_company(self):
        return self.values['-STOCK-'][0][:self.values['-STOCK-'][0].index('-')]

    def get_title(self):
        return self.get_ticker() + ' - ' + self.get_company()

    def get_period(self):
        return self.values['-PERIOD-'][0]

    def is_period_requested(self, period):
        return self.values['-PERIOD-'][0] == period

    def get_period_requested(self):
        return self.values['-PERIOD-'][0]

    def is_50d_mva_requested(self):
        return self.values['-50DMVA-']

    def is_200d_mva_requested(self):
        return self.values['-200DMVA-']

    def is_mva_available(self):
        return not(self.is_period_requested('1d')) and not(self.is_period_requested('5d'))

    def is_mva_requested(self):
        return self.is_50d_mva_requested() or self.is_200d_mva_requested()

    def is_tech_analysis_requested(self):
        return self.values['-RESISTANCE-'] or self.values['-SUPPORT-']

    def is_tech_analysis_available(self):
        return not self.is_period_requested('1d')

    def is_resistance_tech_analysis_requested(self):
        return self.values['-RESISTANCE-']

    def is_support_tech_analysis_requested(self):
        return self.values['-SUPPORT-']

    def is_event_plotting(self):
        return self.event == 'Normal plot' or self.event == 'Candlestick plot'

    def is_stock_chosen(self):
        return self.values['-STOCK-']