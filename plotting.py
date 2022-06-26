from User_Specific import UserSpecific
from extract_financial_data import FinancialData
from graph import Graph

import datetime

import matplotlib
import matplotlib.animation as animation
matplotlib.use('TkAgg')
from matplotlib import style
style.use('ggplot')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

import numpy as np
import pandas as pd


class Plotting():

    def __init__(self):
        self.draw_figure = True
        self.user_specific_obj = None
        self.finance_obj = FinancialData()
        self.ticker = ['^GSPC']  # S&P 500 index
        self.cont_ave = False
        self.period = ['ytd']

        self.f1 = plt.figure(1)
        self.fig_corr = plt.figure(2)
        sp = self.f1.add_subplot(111)
        self.a1_close = [sp]*5
        self.a1_vol = [self.a1_close[0]]*5
        #self.ax_corr = plt.subplot2grid((3, 3), (0, 0), rowspan=3, colspan=3, fig=self.fig_corr)
        self.ax_corr = self.fig_corr.add_subplot(111)

    def append_ticker(self, ticker):
        self.ticker.append(ticker)

    def append_period(self, period):
        self.period.append(period)

    def set_ticker(self, ticker, plot=1):
        self.ticker[plot-1] = ticker
        print('ticker: ', self.ticker)

    def set_period(self, period, plot=1):
        self.period[plot-1] = period

    def cmd_draw_figure(self, ticker='', cont_ave=False, period='ytd'):
        self.draw_figure = True
        self.cont_ave = cont_ave
        print(ticker)

    def set_user_obj(self, user_specific_object):
        self.user_specific_obj = user_specific_object

    def add_to_main_figure(self, functions):  # function is a dict with functions as key and a list as value
        if 'SPECIAL' not in self.ticker:
            df = self.finance_obj.get_stock_history_based_on_period(self.ticker[0], period=self.period[0])
            date = df.index.tolist()
            close = df['Close']
            # volume = df['Volume'] not needed?
            plt.figure(1)  # main figure

            for key, val in functions.items():
                if key == 'simple moving average':
                    for v in val:
                        s = 'SMA_' + str(v)
                        sma = close.rolling(window=int(v)).mean()
                        self.a1_close[1].plot_date(date, sma, label=s, linestyle='-', markersize=1, zorder=2)
                else:
                    print('Function not supported yet: ', key)

    def animate(self, i):

        if self.draw_figure:
            try:
                # As long as the user does not want to see another data it is not needed to draw figure
                # Hence draw_figure goes to False. It will become True when user chooses to view other data.
                self.draw_figure = False
                plt.clf()
                plt.figure(1)  # to make figure be plotted on
                for i in range(len(self.ticker)):
                    plotspan = int(240/self.user_specific_obj.get_plot_number())
                    whitespace_span = max(20, int(plotspan/(self.user_specific_obj.get_plot_number()+1)))
                    print(whitespace_span)
                    graphspan = int(plotspan-whitespace_span)
                    self.a1_close[i] = plt.subplot2grid((250, 4), (graphspan*i+whitespace_span*i, 0),
                                                        rowspan=graphspan, colspan=4)
                    self.a1_close[i].clear()

                    if 'SPECIAL' not in self.ticker[i]:
                        df = self.finance_obj.get_stock_history_based_on_period(self.ticker[i], period=self.period[i])
                        date = df.index.tolist()
                        close = df['Close']
                        volume = df['Volume']

                        self.a1_close[i].plot_date(date, close, label='Close', linestyle='-', markersize=1, zorder=2)
                        if self.cont_ave:
                            df_cont_ave = close.expanding(min_periods=15).mean()
                            self.a1_close[i].plot_date(date, df_cont_ave, label='Continous Average')

                        self.a1_vol[i] = self.a1_close[i].twinx()
                        self.a1_vol[i].fill_between(date, 0, volume, label='Volume', color='lightblue', alpha=0.4,
                                                    zorder=1)

                        self.a1_close[i].xaxis.set_major_formatter(mdates.DateFormatter('%y-%m-%d'))

                        title = self.finance_obj.get_name_from_ticker(self.ticker[i])

                        if self.user_specific_obj.get_plot_number() > 2:
                            self.a1_close[i].legend(bbox_to_anchor=(0, 1.12, 1, .102), loc=3, ncol=2, borderaxespad=0,
                                                    prop={'size': 6})
                            self.a1_vol[i].legend(bbox_to_anchor=(0, 1.02, 0, 0), loc=3, ncol=2, borderaxespad=0,
                                                  prop={'size': 6})
                        else:
                            self.a1_close[i].legend(bbox_to_anchor=(0, 1.12, 1, .102), loc=3, ncol=2, borderaxespad=0,
                                                    prop={'size': 8})
                            self.a1_vol[i].legend(bbox_to_anchor=(0, 1.02, 0, 0), loc=3, ncol=2, borderaxespad=0,
                                                  prop={'size': 8})

                        self.a1_close[i].xaxis.set_major_locator(mticker.MaxNLocator(5))
                        print(len(title))
                        if 14 < len(title) <= 20:
                            fontsize = 12
                        elif len(title) > 20:
                            fontsize = 8
                        else:
                            fontsize = 16
                        self.a1_close[i].set_title(title, fontsize=fontsize)
                        self.a1_close[i].set_ylabel('Close price')
                        self.a1_vol[i].set_ylabel('Volume')

                    elif 'YIELD_CURVE' in self.ticker[i]:

                        def yield_curve_slider(val):
                            pos = slider.val
                            date_string = matplotlib.dates.num2date(pos).strftime('%m/%d/%y')  # strftime converts to str
                            slider.valtext.set_text(date_string)
                            self.a1_close[i].clear()
                            if date_string not in df.index:
                                date_string = get_last_marketday(df, date_string)
                            self.a1_close[i].plot_date(df.columns.values, df.loc[date_string], label='Yield Curve',
                                                       linestyle='-')
                            self.a1_close[i].set_title('Yield Curve')
                            self.a1_close[i].set_ylabel('Yield')
                            self.a1_close[i].set_ylim([y_min, y_max])

                        self.a1_close[i] = plt.subplot2grid((130, 4), (10, 0), rowspan=100, colspan=4)
                        self.a1_vol[i] = plt.subplot2grid((130, 4), (110, 0), rowspan=10, colspan=4)  # for the slider

                        df = self.finance_obj.get_yield_curve()
                        self.a1_close[i].plot_date(df.columns.values, df.iloc[-1], label='Yield Curve', linestyle='-')
                        self.a1_close[i].set_title('Yield Curve')
                        self.a1_close[i].set_ylabel('Yield')

                        x_min = matplotlib.dates.date2num(df.index[0])
                        x_max = matplotlib.dates.date2num(df.index[-1])
                        y_max = df.max(axis='columns').max()
                        y_min = df.min(axis='columns').min()
                        self.a1_close[i].set_ylim([y_min, y_max])

                        today = datetime.datetime.now()
                        today_num = matplotlib.dates.date2num(datetime.datetime.now())
                        yesterday = today - datetime.timedelta(days=1)
                        yesterday_num = matplotlib.dates.date2num(yesterday)
                        delta_t_num = today_num - yesterday_num

                        self.a1_vol[i].axis([x_min, x_max, 0, 5])
                        global slider  # otherwise slider gets unresponsive
                        slider = plt.Slider(ax=self.a1_vol[i], label='Time', valmin=x_min, valmax=x_max,
                                            valinit=x_max, valstep=delta_t_num, facecolor='lightgrey', initcolor='r')
                        slider.valtext.set_text(matplotlib.dates.num2date(x_max).strftime('%m/%d/%y'))
                        slider.valtext.set_rotation(45)
                        slider.on_changed(yield_curve_slider)

            except Exception as e:
                print('Failed because of ', e)

    def correlation_matrix(self, fig, per, x='none'):
        # calculate correlation in shortlist
        shortlist_dict = self.user_specific_obj.get_shortlist()
        print(shortlist_dict)
        df = pd.DataFrame()
        for key in shortlist_dict:
            ticker = shortlist_dict[key]
            print(ticker)
            df_ticker = self.finance_obj.get_stock_history_based_on_period(ticker, period=per)
            df[key] = df_ticker['Close']
        if x == 'none':
            corr_matrix = df.corr()
        else:
            corr_matrix = df.corr()
            corr_graph = Graph()
            for col in corr_matrix.columns:
                low_corr = corr_matrix[(corr_matrix[col] <= float(x)) & (corr_matrix[col] >= -float(x))][col].to_dict()
                print(col)
                print(low_corr)
                print('----------')
                corr_graph.add_vertex(col)
                corr_graph.add_neighbors(col, low_corr)

        # plot correlation
        self.f_corr = fig
        a_corr = plt.subplot2grid((3, 3), (0, 0), rowspan=3, colspan=3, fig=self.f_corr)
        a_corr.matshow(corr_matrix)
        a_corr.set_xticks(np.arange(len(corr_matrix.index.tolist())), labels=corr_matrix.index.tolist(), rotation=45,
                          fontsize='x-small')
        a_corr.set_yticks(np.arange(len(corr_matrix.index.tolist())), labels=corr_matrix.index.tolist(),
                          fontsize='x-small')
        for (i, j), z in np.ndenumerate(corr_matrix):  # to plot values into correlation matrix plot
            a_corr.text(j, i, '{:0.2f}'.format(z), ha='center', va='center',
                        bbox=dict(boxstyle='round', facecolor='white', edgecolor='0.3'))

    def get_correlation_fig(self):
        return self.fig_corr

    def cross_correlation(self, fig, ticker1, ticker2, pb, root):
        # clear axis
        self.fig_corr = fig
        self.fig_corr.clear()
        self.ax_corr = fig.add_subplot(111)

        df_ticker1 = self.finance_obj.get_stock_history_based_on_period(ticker1, 'max')['Close']
        df_ticker2 = self.finance_obj.get_stock_history_based_on_period(ticker2, 'max')['Close']
        length = len(df_ticker1.index)
        x = []
        corr_list = []
        for i in range(length):
            corr = df_ticker1.corr(df_ticker2.shift(-int(length/2)+i))
            corr_list.append(corr)
            x.append(-int(length/2)+i)
            pb['value'] = i/length*100
            root.update_idletasks()

        self.ax_corr.plot(x, corr_list)

    def plot_std(self, years):
        # calculate standard deviation in shortlist
        shortlist_dict = self.user_specific_obj.get_shortlist()
        df_perc = pd.DataFrame()
        if years == 5:
            period = '5y'
        elif years == 10:
            period = '10y'
        for name, ticker in shortlist_dict.items():
            df_ticker = self.finance_obj.get_stock_history_based_on_period(ticker, period)
            df_perc[name] = df_ticker['Close'].pct_change()
        x = df_perc.columns.values
        df_std = df_perc*np.sqrt(253)  # times amount of trading days in a year
        df_mean = df_perc*253

        f_std = plt.figure(3)
        a_std = plt.subplot2grid((3, 3), (0, 0), rowspan=3, colspan=3, fig=f_std)
        a_std.errorbar(x, df_mean.mean(), yerr=[df_std.std(), df_std.std()], fmt='o', capsize=10,
                       elinewidth=1, markeredgewidth=5)
        a_std.set_xticks(np.arange(len(df_std.std().index)), labels=df_std.std().index, rotation=15,
                         fontsize='x-small')
        return f_std

    def plot_backtesting(self, df):

        # 1-base the df['Close'] and df['PaperValue'] to compare growth
        close_first = df.reset_index().iloc[0]['Close']
        paper_value_first = df.reset_index().iloc[0]['PaperValue']
        print(close_first)
        df['Close_1based'] = df['Close'].div(close_first)
        df['PaperValue_1based'] = df['PaperValue'].div(paper_value_first)
        comparison_list = []
        for date, row in df.iterrows():
            comparison_list.append(row['PaperValue_1based']/row['Close_1based'])
        df['Comparison'] = comparison_list

        f_backtesting = plt.figure(4)
        a1_backtesting = plt.subplot2grid((3, 3),(0, 0), rowspan=2, colspan=3, fig=f_backtesting)
        a2_backtesting = plt.subplot2grid((3, 3), (2, 0), rowspan=1, colspan=3, fig=f_backtesting)
        a1_backtesting.plot_date(df.index, df['PaperValue_1based'], label='Algorithm', linestyle='-', markersize=1,
                                 zorder=2)
        a1_backtesting.plot_date(df.index, df['Close_1based'], label='Close', linestyle='-', markersize=1, zorder=2)
        a2_backtesting.plot_date(df.index, df['Comparison'], label='Algorithm/Passive', linestyle='-', markersize=1,
                                 zorder=2)
        a1_backtesting.legend()
        a2_backtesting.legend()

        return f_backtesting

    def plot_optimization(self, df, ma_opt):
        f_optimization = plt.figure(5)
        a_optimization = plt.subplot2grid((3, 3), (0, 0), rowspan=3, colspan=3, fig=f_optimization)
        a_optimization.plot(df['ma_opt'], df['PaperValue'], label='Optimzation of ma', linestyle='-', markersize=1,
                                 zorder=2)
        a_optimization.legend()
        a_optimization.set_title('Optimal ma: ' + str(ma_opt))

        return f_optimization

    def plot_df(self, df):
        f_df = plt.figure(6)
        a_df = plt.subplot2grid((3, 3), (0, 0), rowspan=3, colspan=3, fig=f_df)
        a_df.plot(df, label=df.columns, linestyle='-', markersize=1)
        a_df.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        a_df.set_yticklabels(['{:.0f}'.format(x/1000000) for x in a_df.get_yticks()])
        a_df.legend()
        a_df.set_ylabel('[In millions]')

        return f_df


def get_last_marketday(df, date_string):
    if date_string in df.index:
        return date_string
    else:
        date_dt = datetime.datetime.strptime(date_string, '%m/%d/%y')
        date_dt = date_dt - datetime.timedelta(days=1)
        date_string = date_dt.strftime('%m/%d/%y')
        return get_last_marketday(df, date_string)
