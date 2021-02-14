import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, FigureCanvasAgg, NavigationToolbar2Tk
from matplotlib import style, font_manager
from matplotlib.dates import DateFormatter, num2date
from matplotlib.widgets import MultiCursor
import mplfinance as mpf
import datetime
from extract_financial_data import get_date_from_period
from technical_analysis import TechnicalAnalysis
import numpy as np
import matplotlib.ticker as mticker


# For periods to chose in gui:
PERIOD_DEF = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']

# Fonts used in cutomization of plots:
font_title = {'family': 'Courier New',
              'color': '#822304',
              'weight': 'heavy',
              'size': 25,
              }
font_xylabel = {'family': 'Courier New',
                'color': '#8787a1',
                'weight': 'light',
                'size': 16,
                }
font_cursor = {'family': 'Courier New',
               'style': 'italic',
               'color': '#303d34',
               'weight': 'bold',
               'size': 15,
               }


class Gui:

    def __init__(self, financial_data_object):
        # Initialize attributes:
        self.event = ''
        self.values = 0
        self.fig = 0
        self.figure_canvas_agg = 0
        self.axlist = []
        self.volume = 0
        self.close_price = 0
        self.multicursor = 0
        self.technical_analysis_object = 0
        self.financial_data_object = financial_data_object

        # Initialize gui layout
        self.layout = [
            [sg.Listbox(values=self.financial_data_object.readable_stock_list, size=(40, 50), key='-STOCK-'),
             sg.VSeparator(), sg.Column(
                layout=[[sg.Canvas(key='fig_cv', size=(400 * 3, 400 * 2))]],
                background_color='#DAE0E6',
                pad=(0, 0)),
             sg.Listbox(values=PERIOD_DEF, default_values='ytd', size=(5, 11), key='-PERIOD-')],

            [sg.Canvas(key='-TOOLBOX-', pad=((350, 3), 0))],

            [sg.Button('Normal plot'), sg.Button('Candlestick plot'), sg.Button('Exit'),
             sg.Checkbox('50 days moving average', default=False, key='-50DMOVAVE-', pad=((300, 3,), 0)),
             sg.Checkbox('200 days moving average', default=False, key='-200DMOVAVE-'),
             sg.Checkbox('Support levels', default=False, key='-SUPPORT-'),
             sg.Checkbox('Resistance levels', default=False, key='-RESISTANCE-')],
        ]

        # Initialize gui window
        self.window = sg.Window('Investment Helper', self.layout, resizable=True)
        self.window.Finalize()
        self.window.Maximize()

    def start(self):
        while True:
            self.event, self.values = self.window.read()
            print('event: ', self.event)
            print('values: ', self.values)
            if self.event in (sg.WIN_CLOSED, 'Exit'):
                break
            if self.event == 'Normal plot':
                if not self.values['-STOCK-']:
                    sg.popup('You need to choose a stock before plotting!')
                else:
                    #  MATPLOTLIB
                    self.create_plot()
                    self.draw_canvas()
            if self.event == 'Candlestick plot':
                if not self.values['-STOCK-']:
                    sg.popup('You need to choose a stock before plotting!')
                else:
                    # CANDLESTICK PLOT
                    self.create_candlestick_plot()
                    self.draw_canvas()
        self.window.close()

    def draw_canvas(self):
        # To destroy figure and toolbox that were drawed to gui before:
        if self.window['fig_cv'].TKCanvas.children:
            for child in self.window['fig_cv'].TKCanvas.winfo_children():
                child.destroy()
        if self.window['-TOOLBOX-'].TKCanvas.children:
            for child in self.window['-TOOLBOX-'].TKCanvas.winfo_children():
                child.destroy()

        # FigureCanvasTkAgg is embedding the figure to the tkinter canvas
        self.figure_canvas_agg = FigureCanvasTkAgg(self.fig, master=self.window['fig_cv'].TKCanvas)
        self.figure_canvas_agg.draw()

        # Create a cursor for axlist. Needs to be attribute to be responsive.
        # useblit makes the performance much better.
        self.multicursor = MultiCursor(self.figure_canvas_agg, self.axlist, lw=1, useblit=True)

        # function read_cursor_value is called while hovering over the canvas
        self.figure_canvas_agg.mpl_connect('motion_notify_event', self.read_cursor_value)

        # Embeds toolbar to tkinter canvas
        toolbar = NavigationToolbar2Tk(self.figure_canvas_agg, self.window['-TOOLBOX-'].TKCanvas)
        toolbar.update()

        # Packing the canvas to tkinter
        self.figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=True)

    def read_cursor_value(self, coord):
        # To clear earlier texts from self.ax1.texts
        self.axlist[0].texts = []

        # get mouse coordinates
        if not coord.inaxes:
            return

        if self.event == 'Normal plot':

            # In normal plot the event.xdata is epoch time
            x = num2date(int(coord.xdata)).replace(tzinfo=None)

            # Finds the closest value on x-axis as index
            i = np.searchsorted(self.close_price.index, [x])[0]

        elif self.event == 'Candlestick plot':
            i = int(coord.xdata)

        # Make sure that the index i is in range:
        if i >= len(self.close_price.index):
            i = len(self.close_price.index) - 1
        elif i < 0:
            i = 0

        price = "{:.2f}".format(self.close_price.iloc[i])
        volume = self.volume.iloc[i]
        cursor_value = 'price: ' + str(price) + ', volume: ' + str(volume)

        self.axlist[0].text(x=0.3, y=1.05, s=cursor_value, fontdict=font_cursor, transform=self.axlist[0].transAxes)
        self.figure_canvas_agg.draw()

    def create_plot(self):
        # Close all older figures to clear window:
        plt.close('all')
        self.axlist.clear()

        # Use style:
        style.use('seaborn-darkgrid')

        # Initialize figure:
        self.fig = plt.figure(1)
        dpi = self.fig.get_dpi()

        # Get correct date format
        formatter = get_formatter(self.values['-PERIOD-'][0])

        # Create axes:
        self.axlist.append(plt.subplot2grid((6, 1), (0, 0), rowspan=4, colspan=1))
        self.axlist.append(plt.subplot2grid((6, 1), (5, 0), rowspan=1, colspan=1, sharex=self.axlist[0]))

        # Set fig size:
        self.fig.set_size_inches(404 * 2 / float(dpi), 404 / float(dpi))

        # Get financial data to work with:
        ticker = self.financial_data_object.get_ticker_from_readable_stock(self.values['-STOCK-'][0])
        df = self.financial_data_object.get_stock_history_based_on_period(ticker, self.values['-PERIOD-'][0])
        self.close_price = df['Close']
        self.volume = df['Volume']

        # Plot data in axes:
        self.axlist[0].plot_date(self.close_price.index, self.close_price.values, '-', linewidth=2)
        self.axlist[1].plot_date(self.volume.index, self.volume.values, '-', linewidth=0.8)
        self.axlist[1].xaxis.set_major_formatter(formatter)
        for label in self.axlist[1].xaxis.get_ticklabels():
            label.set_rotation(45)
        self.axlist[1].fill_between(self.volume.index, self.volume)

        # Customization of axes:
        self.axlist[0].set_ylabel('Close Price [$]', fontdict=font_xylabel)
        self.axlist[0].set_title(ticker + ' - ' + self.values['-STOCK-'][0][:self.values['-STOCK-'][0].index('-')],
                                 pad=45, fontdict=font_title)
        self.axlist[0].yaxis.set_label_coords(-0.1, 0.5)
        self.axlist[1].set_ylabel('Volume', fontdict=font_xylabel)
        self.axlist[1].yaxis.set_label_coords(-0.1, 0.5)
        self.axlist[1].yaxis.set_major_formatter(mticker.FormatStrFormatter('%d'))
        plt.setp(self.axlist[0].get_xticklabels(), visible=False)
        plt.subplots_adjust(left=0.125, bottom=0.171, right=0.9, top=0.88, wspace=0.2, hspace=-0.4)

        #--- MOVING AVERAGE CALCULATIONS---:

        # Check if period has moving average available:
        if self.values['-PERIOD-'][0] != '1d' and self.values['-PERIOD-'][0] != '5d' \
                and self.values['-PERIOD-'][0] != '1m':  # moving average not available for period 1d, 5d and 1mo.

            # 50 days moving average:
            if self.values['-50DMOVAVE-']:
                if self.values['-PERIOD-'][0] != 'max':
                    # to get the startdate for the mov ave calculation
                    # and get the df back to that date to get mov ave over whole range.
                    startdate = get_date_from_period(self.values['-PERIOD-'][0], 50)
                    df = self.financial_data_object.get_stock_history_based_on_dates(ticker, startdate, datetime.date.today())
                    close_price_mov_ave = df['Close']
                else:
                    # if period = max the moving average calculation starts at the first trade day.
                    close_price_mov_ave = self.close_price

                # Calculate 50 days rolling moving average:
                rolling_mean_50 = close_price_mov_ave.rolling(window=50).mean()

                # Plot 50 days moving average in ax
                self.axlist[0].plot(rolling_mean_50, label='50 days moving average', linewidth=0.8)
                self.axlist[0].legend(loc='best', fontsize='small')

            # 200 days moving average
            if self.values['-200DMOVAVE-']:
                if self.values['-PERIOD-'][0] != 'max':
                    # to get the startdate for the mov ave calculation
                    # and get the df back to that date to get mov ave over whole range.
                    startdate = get_date_from_period(self.values['-PERIOD-'][0], 200)
                    df = self.financial_data_object.get_stock_history_based_on_dates(ticker, startdate, datetime.date.today())
                    close_price_mov_ave = df['Close']
                else:
                    # if period = max the moving average calculation starts at the first trade day.
                    close_price_mov_ave = self.close_price

                # Calculate 200 days rolling moving average:
                rolling_mean_200 = close_price_mov_ave.rolling(window=200).mean()

                # Plot 200 days moving average in ax
                self.axlist[0].plot(rolling_mean_200, label='200 days moving average', linewidth=0.8)
                self.axlist[0].legend(loc='best', fontsize='small')

        #---RESISTANCE AND SUPPORT LEVELS---:

        # Initialize technical analysis object
        self.technical_analysis_object = TechnicalAnalysis(ticker)

        # Get resistance levels:
        if self.values['-RESISTANCE-'] and self.values['-PERIOD-'][0] != '1d':

            # Find resistance levels based on resistance threshold
            # Resistance threshold: a the maximum acceptable change of a price
            # to still count as the same resistance level.
            self.technical_analysis_object.find_resistance_levels(df, resistance_threshold=0.01)

            # Get the closest resistance levels to todays price: (max 3 resistance levels)
            resistance_df = self.technical_analysis_object.get_closest_resistance_levels()

            # Plot resistance lines in ax:
            for date in resistance_df.index:
                self.axlist[0].hlines(resistance_df.loc[date, 'High'], date, datetime.date.today(),
                                      colors='red', linewidths=0.5)

        # Get support levels:
        if self.values['-SUPPORT-'] and self.values['-PERIOD-'][0] != '1d':

            # Find support levels based on support threshold
            # Support threshold: a the maximum acceptable change of a price
            # to still count as the same support level.
            self.technical_analysis_object.find_support_levels(df, support_threshold=0.01)

            # Get the closest support levels to todays price: (max 3 support levels)
            support_df = self.technical_analysis_object.get_closest_support_levels()

            # Plot support lines in ax:
            for date in support_df.index:
                self.axlist[0].hlines(support_df.loc[date, 'Low'], date, datetime.date.today(), colors='green', linewidths=0.5)


    def create_candlestick_plot(self):

        # Close all older figures to clear window:
        plt.close('all')

        # Initialize parameters:
        mov_ave = []
        legend_text = []
        alines_list = []
        colors_for_alines = []

        # Get financial data to work with:
        #  df = [['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        ticker = self.financial_data_object.get_ticker_from_readable_stock(self.values['-STOCK-'][0])
        df = self.financial_data_object.get_stock_history_based_on_period(ticker, self.values['-PERIOD-'][0])
        self.close_price = df['Close']
        self.volume = df['Volume']

        #---MOVING AVERAGE PREPARATIONS---:

        # Append(extend) into mov_ave list which moving averages the user is interested in:
        if self.values['-50DMOVAVE-'] and self.values['-200DMOVAVE-']:
            mov_ave.extend([50, 200])
            legend_text.extend(['50 days mov ave', '200 days mov ave'])
        elif self.values['-50DMOVAVE-']:
            mov_ave.append(50)
            legend_text.append('50 days mov ave')
        elif self.values['-200DMOVAVE-']:
            mov_ave.append(200)
            legend_text.append('200 days mov ave')

        #---RESISTANCE AND SUPPORT LEVELS---:

        # Initialize technical analysis object
        self.technical_analysis_object = TechnicalAnalysis(ticker)

        # Resistance levels:
        if self.values['-RESISTANCE-'] and self.values['-PERIOD-'][0] != '1d':

            # Find resistance levels based on resistance threshold
            # Resistance threshold: a the maximum acceptable change of a price
            # to still count as the same resistance level.
            self.technical_analysis_object.find_resistance_levels(df, resistance_threshold=0.01)

            # Get the closest resistance levels to todays price: (max 3 resistance levels)
            resistance_df = self.technical_analysis_object.get_closest_resistance_levels()

            # Get latest trading day. Used to create resistance lines.
            latest_trading_day = df.index[-1]

            # Append resistance levels into alines for plotting later:
            for date in resistance_df.index:
                alines_list.append(
                    [(date, resistance_df.loc[date, 'High']), (latest_trading_day, resistance_df.loc[date, 'High'])])
                colors_for_alines.append('red')

        # Support levels:
        if self.values['-SUPPORT-'] and self.values['-PERIOD-'][0] != '1d':

            # Find support levels based on support threshold
            # Support threshold: a the maximum acceptable change of a price
            # to still count as the same support level.
            self.technical_analysis_object.find_support_levels(df, support_threshold=0.01)

            # Get the closest support levels to todays price: (max 3 support levels)
            support_df = self.technical_analysis_object.get_closest_support_levels()

            # Get latest trading day. Used to create support lines.
            latest_trading_day = df.index[-1]

            # Append resistance levels into alines for plotting later:
            for date in support_df.index:
                alines_list.append(
                    [(date, support_df.loc[date, 'Low']), (latest_trading_day, support_df.loc[date, 'Low'])])
                colors_for_alines.append('green')

        # Plot a candlestick plot to figure and axlist
        width_config = {'volume_width': 0.525}
        self.fig, self.axlist = mpf.plot(df, type='candle', figratio=(9, 6), returnfig=True, volume=True,
                                         style='yahoo', mav=mov_ave, update_width_config=width_config,
                                         alines=dict(alines=alines_list, colors=colors_for_alines, linewidths=0.5))

        # Customize axes:
        self.fig.subplots_adjust(hspace=0.5)
        self.axlist[0].legend(legend_text, loc='best', fontsize='small')
        self.axlist[0].set_title(ticker + ' - ' + self.values['-STOCK-'][0][:self.values['-STOCK-'][0].index('-')],
                                 pad=45, fontdict=font_title)
        self.axlist[0].set_ylabel('Open, High, Low, Close', fontdict=font_xylabel)
        self.axlist[0].yaxis.set_ticks_position("left")
        self.axlist[0].yaxis.set_label_coords(-0.14, 0.5)

        # By some reason axlist has length 4 and axlist[2] is the volume graph.
        self.axlist[2].set_ylabel('Volume', fontdict=font_xylabel)
        self.axlist[2].yaxis.set_ticks_position("left")
        self.axlist[2].yaxis.set_label_coords(-0.14, 0.5)
        self.axlist[2].yaxis.set_major_formatter(mticker.FormatStrFormatter('%d'))


# Get dateformatter based on period chosen:
def get_formatter(period):
    if period == '1d':
        return DateFormatter('%H-%M')
    elif period == 'ytd':
        return DateFormatter('%b-%d')
    else:
        return DateFormatter('%Y-%b-%d')



