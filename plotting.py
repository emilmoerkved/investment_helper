# External modules:
import datetime
from matplotlib import style
from matplotlib.dates import DateFormatter, num2date
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import mplfinance as mpf
import numpy as np

# Internal modules:
from extract_financial_data import get_date_from_period, FinancialData


class Plotting:
    # class for the plotting of the figure and axlists requested from user.

    def __init__(self):
        # Fonts used in customization of plots:
        self._font_title = {'family': 'Courier New',
                           'color': '#822304',
                           'weight': 'heavy',
                           'size': 25,
                           }
        self._font_xylabel = {'family': 'Courier New',
                             'color': '#8787a1',
                             'weight': 'light',
                             'size': 16,
                             }
        self._font_cursor = {'family': 'Courier New',
                            'style': 'italic',
                            'color': '#303d34',
                            'weight': 'bold',
                            'size': 15,
                            }
        self._df = None
        self._financial_data_object = None
        self._axlist = []
        self._fig = None
        self._scat = None
        self._user_input = None

    def set_user_input(self, user_input):
        self._user_input = user_input

    def _set_df(self, df):
        self._df = df

    def plot(self):
        if self._user_input.event == 'Normal plot':
            return self._create_normal_plot()
        elif self._user_input.event == 'Candlestick plot':
            return self._create_candlestick_plot()
        else:
            raise NameError('Does not recognize event!')

    def _clear_figure(self):
        # Close all older figures to clear window:
        plt.close('all')
        self._axlist.clear()

    def _plot_mva(self):
        mva_list = self._get_mva_list()
        for mva in mva_list:
            self._axlist[0].plot(self._get_mva_df(mva).rolling(window=mva).mean(), label=self._create_mva_label(mva),
                                 linewidth=0.8)
        self._axlist[0].legend(loc='best', fontsize='small')  # Should this be here?

    def _plot_technical_analysis(self):
        if self._user_input.is_support_tech_analysis_requested():
            self._plot_support_tech_analysis()
        if self._user_input.is_resistance_tech_analysis_requested():
            self._plot_resistance_tech_analysis()

    def _plot_resistance_tech_analysis(self):
        self._financial_data_object.technical_analysis.find_resistance_levels(resistance_threshold=0.01)
        resistance_df = self._financial_data_object.technical_analysis.get_closest_resistance_levels()
        for date in resistance_df.index:
            self._axlist[0].hlines(resistance_df.loc[date, 'High'], date, datetime.date.today(),
                                   colors='red', linewidths=0.5)

    def _plot_support_tech_analysis(self):
        self._financial_data_object.technical_analysis.find_support_levels(support_threshold=0.01)
        support_df = self._financial_data_object.technical_analysis.get_closest_support_levels()
        for date in support_df.index:
            self._axlist[0].hlines(support_df.loc[date, 'Low'], date, datetime.date.today(),
                                   colors='green', linewidths=0.5)

    ###################      Normal plot          #########################

    def _create_normal_plot(self):
        self._clear_figure()
        self._initialize_normal_figure()

        self._financial_data_object = FinancialData(self._user_input.get_ticker())
        self._set_df(self._financial_data_object.get_stock_df_by_period(self._user_input.get_period()))
        if self._is_df_empty():  # possible if company is delisted for example.
            self._set_title_delisted_company()
            return self._fig, self._axlist  # empty figure but title updated

        self._plot_data_normal()
        self._customize_axes_normal()

        # moving average:
        if self._user_input.is_mva_available() and self._user_input.is_mva_requested():
            self._plot_mva()

        # technical analysis:
        if self._user_input.is_tech_analysis_available() and self._user_input.is_tech_analysis_requested():
            self._financial_data_object.technical_analysis.set_df(self._df)
            self._plot_technical_analysis()

        return self._fig, self._axlist

    def _initialize_normal_figure(self):
        # Use style:
        style.use('seaborn-darkgrid')

        self._fig = plt.figure()
        dpi = self._fig.get_dpi()  # dpi is dots per square inches. Controls the resolution. Default is 100.

        self._axlist.append(plt.subplot2grid((6, 1), (0, 0), rowspan=4, colspan=1))
        self._axlist.append(plt.subplot2grid((6, 1), (5, 0), rowspan=1, colspan=1, sharex=self._axlist[0]))

        self._fig.set_size_inches(404 * 2 / float(dpi), 404 / float(dpi))

    def _is_df_empty(self):
        return len(self._df) == 0

    def _set_title_delisted_company(self):
        self._axlist[0].set_title(self._user_input.get_title() + ' possible delisted!', pad=45,
                                  fontdict=self._font_title)

    def _plot_data_normal(self):
        self._axlist[0].plot_date(self._df['Close'].index, self._df['Close'].values, '-', linewidth=2)
        self._axlist[1].plot_date(self._df['Volume'].index, self._df['Volume'].values, '-', linewidth=0.8)

    def _customize_axes_normal(self):
        self._axlist[0].set_title(self._user_input.get_title(), pad=45, fontdict=self._font_title)
        self._axlist[0].set_ylabel('Close Price [$]', fontdict=self._font_xylabel)
        self._axlist[0].yaxis.set_label_coords(-0.1, 0.5)
        self._axlist[1].xaxis.set_major_formatter(get_formatter(self._user_input.get_period()))
        self._axlist[1].set_ylabel('Volume', fontdict=self._font_xylabel)
        self._axlist[1].yaxis.set_label_coords(-0.1, 0.5)
        self._axlist[1].yaxis.set_major_formatter(mticker.FormatStrFormatter('%d'))
        self._axlist[1].fill_between(self._df['Volume'].index, self._df['Volume'])

        for label in self._axlist[1].xaxis.get_ticklabels():
            label.set_rotation(45)

        plt.setp(self._axlist[0].get_xticklabels(), visible=False)  # make x-axis on axlist[0] invisible

        plt.subplots_adjust(left=0.125, bottom=0.171, right=0.9, top=0.88, wspace=0.2, hspace=-0.4)

    #######################              Candlestick plot              ###################################

    def _create_candlestick_plot(self):
        self._clear_figure()

        legndtxt_mva_list = []

        self._financial_data_object = FinancialData(self._user_input.get_ticker())
        self._set_df(self._financial_data_object.get_stock_df_by_period(self._user_input.get_period()))

        self._plot_candlestick()

        # moving average:
        if self._user_input.is_mva_available() and self._user_input.is_mva_requested():
            mva_list = self._get_mva_list()
            legndtxt_mva_list = self._get_legndtxt_mva_list(mva_list)
            self._plot_mva_candlestick(mva_list)

        # technical analysis:
        if self._user_input.is_tech_analysis_available() and self._user_input.is_tech_analysis_requested():
            self._financial_data_object.technical_analysis.set_df(self._df)
            self._plot_tech_analysis_candlestick()

        self._customize_axes_candlestick(legndtxt_mva_list)

        return self._fig, self._axlist

    def _plot_candlestick(self):
        self._fig, self._axlist = mpf.plot(self._df, type='candle', figratio=(9, 6), returnfig=True, volume=True,
                                           style='yahoo', update_width_config={'volume_width': 0.525})

    def _get_mva_list(self):
        mva_list = []
        if self._user_input.is_50d_mva_requested():
            mva_list.append(50)
        if self._user_input.is_200d_mva_requested():
            mva_list.append(200)
        return mva_list

    def _get_legndtxt_mva_list(self, mva_list):
        legndtxt_list = []
        for mva in mva_list:
            legndtxt_list.append(str(mva) + ' days mov ave')
        return legndtxt_list

    def _create_mva_label(self, mva_len):
        return str(mva_len) + ' days moving average'

    def _plot_mva_candlestick(self, mva_list):
        for mva in mva_list:
            self._axlist[0].plot(
                self._get_mva_df(mva=mva).rolling(window=mva).mean().dropna().reset_index()['Close'],
                label=self._create_mva_label(mva), linewidth=0.8)

    def _get_mva_df(self, mva):
        if self._user_input.get_period() == 'max':
            return self._df['Close']  # if period is max the df will be all data
        else:
            start_date = get_date_from_period(self._user_input.get_period(), mva)
            # start date will be the number of days mva before start of df.
        return self._financial_data_object.get_stock_df_by_dates(start_date, datetime.date.today())['Close']

    def _plot_tech_analysis_candlestick(self):
        df_indexed = self._df.reset_index()
        latest_trading_day = df_indexed.index[-1]
        if self._user_input.is_resistance_tech_analysis_requested():
            self._plot_resistance_tech_analysis_candlestick(df_indexed, latest_trading_day)
        if self._user_input.is_support_tech_analysis_requested():
            self._plot_support_tech_analysis_candlestick(df_indexed, latest_trading_day)

    def _plot_resistance_tech_analysis_candlestick(self, df_indexed, latest_trading_day):
        self._financial_data_object.technical_analysis.find_resistance_levels(resistance_threshold=0.01)
        resistance_df = self._financial_data_object.technical_analysis.get_closest_resistance_levels()
        for date in resistance_df.index:
            ind_start = df_indexed.loc[df_indexed['Date'] == date].index.values[-1]
            self._axlist[0].hlines(resistance_df.loc[date, 'High'], ind_start, latest_trading_day,
                                   colors='red', linewidths=0.5)

    def _plot_support_tech_analysis_candlestick(self, df_indexed, latest_trading_day):
        self._financial_data_object.technical_analysis.find_support_levels(support_threshold=0.01)
        support_df = self._financial_data_object.technical_analysis.get_closest_support_levels()
        for date in support_df.index:
            ind_start = df_indexed.loc[df_indexed['Date'] == date].index.values[-1]
            self._axlist[0].hlines(support_df.loc[date, 'Low'], ind_start, latest_trading_day,
                                   colors='green', linewidths=0.5)

    def _customize_axes_candlestick(self, legndtxt_mva_list):
        self._fig.subplots_adjust(hspace=0.5)
        self._axlist[0].legend(legndtxt_mva_list, loc='best', fontsize='small')
        self._axlist[0].set_title(self._user_input.get_title(), pad=45, fontdict=self._font_title)
        self._axlist[0].set_ylabel('Open, High, Low, Close', fontdict=self._font_xylabel)
        self._axlist[0].yaxis.set_ticks_position("left")
        self._axlist[0].yaxis.set_label_coords(-0.14, 0.5)

        # By some reason axlist has length 4 and axlist[2] is the volume graph.
        self._axlist[2].set_ylabel('Volume', fontdict=self._font_xylabel)
        self._axlist[2].yaxis.set_ticks_position("left")
        self._axlist[2].yaxis.set_label_coords(-0.14, 0.5)
        self._axlist[2].yaxis.set_major_formatter(mticker.FormatStrFormatter('%d'))

    ######################                Cursor                  #############################

    def create_cursor_value(self, mouse):
        self._clear_cursor_text()
        if mouse.inaxes:
            self._turn_off_autoscale()  # So that zooming is possible while the plot gets updated.
            self._update_scatter(mouse)
            self._update_cursor(mouse)
            self._clear_scatter()

    def _turn_off_autoscale(self):
        for ax in self._axlist:
            ax.autoscale(False)

    def _clear_cursor_text(self):
        self._axlist[0].texts = []  # To clear earlier texts from self.ax1.texts

    def _clear_scatter(self):
        if self._scat is not None:
            self._scat.remove()
            self._scat = None

    def _update_scatter(self, mouse):
        if self._user_input.event == 'Normal plot':
            self._plot_scatter_on_cursor(self._get_x_pos_from_epoch_coord(mouse))
        elif self._user_input.event == 'Candlestick plot':
            self._plot_scatter_on_cursor(self._get_index_in_range_from_coord(mouse))

    def _plot_scatter_on_cursor(self, i):
        if 0 < i <= len(self._df['Close'].index) - 1:
            if self._user_input.event == 'Normal plot':  # normal plot has datetime as x-axis
                x = self._df['Close'].index[i]
                print(x)
            elif self._user_input.event == 'Candlestick plot':  # candlestick plot has index as x-axis
                x = i
            self._scat = self._axlist[0].scatter([x], [self._df['Close'].iloc[i]], marker='o', s=80, color='gold')

    def _get_x_pos_from_epoch_coord(self, mouse):
        x = num2date(int(mouse.xdata)).replace(tzinfo=None)
        return np.searchsorted(self._df['Close'].index, [x])[0]

    def _get_index_in_range_from_coord(self, mouse):
        if self._user_input.event == 'Normal plot':
            x_pos = self._get_x_pos_from_epoch_coord(mouse)
        else:
            x_pos = int(mouse.xdata)
        if x_pos >= len(self._df['Close'].index):
            return len(self._df['Close'].index) - 1
        elif x_pos < 0:
            return 0
        else:
            return x_pos

    def _update_cursor(self, mouse):
        self._axlist[0].text(x=0.3, y=1.05, s=self._get_cursor_text(mouse), fontdict=self._font_cursor,
                             transform=self._axlist[0].transAxes)
        mouse.canvas.draw()

    def _get_cursor_text(self, mouse):
        price = "{:.2f}".format(self._df['Close'].iloc[self._get_index_in_range_from_coord(mouse)])
        volume = self._df['Volume'].iloc[self._get_index_in_range_from_coord(mouse)]
        return 'price: ' + str(price) + ', volume: ' + str(volume)


# Get dateformatter based on period chosen:
def get_formatter(period):
    if period == '1d':
        return DateFormatter('%H-%M')
    elif period == 'ytd':
        return DateFormatter('%b-%d')
    else:
        return DateFormatter('%Y-%b-%d')