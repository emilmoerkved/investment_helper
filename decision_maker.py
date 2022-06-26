import pandas as pd
import re

from extract_financial_data import FinancialData


class Decision:

    def __init__(self, df):
        self.df = df
        self.financial_obj = FinancialData()

    def make_decision(self, buy_cond, sell_cond):
        # options: close price, simple moving average(x)
        # .Clp = close price, .MovAve(x) = simple moving average(x)
        # example buy_condition: ^GLF.Clp > ^GLF.MovAve(50)
        # 'Close' should already be included in the df
        # If MovAve is in the condition we need to add it to the df
        #print('buy condition: ', buy_cond)
        #print('sell condition: ', sell_cond)
        ma_pattern = re.compile(r'\d+')
        ma_x = list(set(ma_pattern.findall(buy_cond+sell_cond)))
        # used list(set(..) to remove duplicates. probably possible in regex also but could not find the solution.

        for x in ma_x:
            col = 'MA_'+str(x)
            self.df[col] = self.df['Close'].rolling(window=int(x)).mean()

        # get function for buy and sell condition
        buy_cond = self.get_condition_function(buy_cond)
        sell_cond = self.get_condition_function(sell_cond)
        #print(sell_cond)

        decision_list = []
        for date, row in self.df.iterrows():
            if eval(buy_cond):
                decision_list.append('Buy')
            elif eval(sell_cond):
                decision_list.append('Sell')
            else:
                decision_list.append('-')

        return decision_list

    def get_condition_function(self, cond):
        # extract math symbol
        # extract ticker
        # extract value func

        sup_func_pattern_clp = re.compile(r'Clp')
        sup_func_pattern_mvav = re.compile(r'MvAv')
        supported_functions = {sup_func_pattern_clp: 'Close',
                               sup_func_pattern_mvav: 'MA_'}

        # example buy_condition: ^GSPC.Clp > ^GSPC.MvAv(50) -> df['Close'] > df['MA_50']

        # remove white space:
        cond = self.clear_whitespace(cond)

        for key, val in supported_functions.items():
            cond = re.sub(key, val, cond)

        par_pattern = re.compile(r'[()]')
        cond = re.sub(par_pattern, '', cond)

        # split string on "and" "or", then splitting on math expressions
        and_or_pattern = re.compile(r'(and|or)', re.IGNORECASE)
        math_pattern = re.compile(r'([<>=])')

        return_string = ''

        for expr in and_or_pattern.split(cond):
            #print(expr)
            for val in math_pattern.split(expr):
                #print(val)
                if '.' in val:
                    return_string += 'row[\'' + val[val.rfind('.')+1:] + '\']'
                else:
                    return_string += ' ' + val + ' '

        return return_string

    def get_range_of_optimization_function(self, cond):
        cond = self.clear_whitespace(cond)
        opt_pattern = re.compile('Opt_f\[\d+\,\d+\]')
        opt_match = re.search(opt_pattern, cond).group(0)
        return re.findall('[0-9]+', opt_match)

    def clear_whitespace(self, string):
        whitespace_pattern = re.compile(r'\s')
        return re.sub(whitespace_pattern, '', string)

    def fill_in_ma(self, cond, x):
        cond = self.clear_whitespace(cond)
        opt_pattern = re.compile('Opt_f\[\d+\,\d+\]')
        return re.sub(opt_pattern, str(x), cond)





