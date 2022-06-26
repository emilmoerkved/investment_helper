class UserSpecific:

    def __init__(self):
        self.shortlist = {'S&P 500': '^GSPC',
                          'Nasdaq Composite': '^IXIC',
                          'Ten year Treasury yield': '^TNX',
                          'Gold': 'GC=F',
                          'Bitcoin': 'BTC-USD',
                          'Microsoft': 'MSFT'}
        self.plot_number = 1
        self.algorithm = {'Buy Condition': '',
                          'Sell Condition': ''}

        # Technical analysis:
        self.simple_mov_ave_days = []
        self.exp_mov_ave_days = []
        self.rsi = []
        self.bollinger_band = []
        self.functions = {'simple moving average': self.simple_mov_ave_days,
                          'exponential moving average': self.exp_mov_ave_days,
                          'relative strength index': self.rsi,
                          'bollinger bands': self.bollinger_band}
        self.supported_functions = ['simple moving average', 'exponential moving average', 'relative strength index',
                                    'bollinger bands']

    def set_shortlist(self, shortlist):
        self.shortlist = shortlist

    def get_shortlist(self):
        return self.shortlist

    def set_plot_number(self, plot_number):
        self.plot_number = plot_number

    def get_plot_number(self):
        return self.plot_number

    def set_algorithm(self, buy_cond, sell_cond):
        self.algorithm['Buy Condition'] = buy_cond
        self.algorithm['Sell Condition'] = sell_cond

    def get_supported_functions(self):
        return self.supported_functions

    def append_to_function(self, days, function=''):
        if function != '':
            self.functions[function].append(days)
        else:
            print('Function not supported ', function)

    def clear_function(self, function=''):
        if function != '':
            self.functions[function].clear()
        else:
            print('Function not supported ', function)

    def remove_from_function(self, number, function=''):
        if function != '':
            self.functions[function].remove(number)
        else:
            print('Function not supported ', function)

    def tech_analysis_string(self):
        s = ''
        for key, val in self.functions.items():
            if val:
                s += key + '\n'
                for v in val:
                    s += str(v) + ' days\n'
        return s