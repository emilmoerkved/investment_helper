import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, FigureCanvasAgg, NavigationToolbar2Tk
import matplotlib.ticker as mticker
from matplotlib import style
from matplotlib.dates import DateFormatter
import mplfinance as mpf
import datetime
from extract_financial_data import get_date_from_period
from technical_analysis import TechnicalAnalysis


def draw_figure_w_toolbar(canvas, fig, canvas_toolbar):
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    if canvas_toolbar.children:
        for child in canvas_toolbar.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)
    toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)


class Toolbar(NavigationToolbar2Tk):
    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)


def create_gui(financial_data):
    period_def = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']

    layout = [
        [sg.Listbox(values=financial_data.readable_stock_list, size=(40, 50), key='-STOCK-'),
         sg.VSeparator(), sg.Column(
            layout=[[sg.Canvas(key='fig_cv', size=(400 * 3, 400*2))]],
            background_color='#DAE0E6',
            pad=(0, 0)),
         sg.Listbox(values=period_def, default_values='ytd', size=(5, 11), key='-PERIOD-')],

        [sg.Canvas(key='-TOOLBOX-', pad=((300, 3), 0))],

        [sg.Button('Normal plot'), sg.Button('Candlestick plot'), sg.Button('Exit'),
         sg.Checkbox('50 days moving average', default=False, key='-50DMOVAVE-', pad=((300, 3,), 0)),
         sg.Checkbox('200 days moving average', default=False, key='-200DMOVAVE-'),
         sg.Checkbox('Support levels', default=False, key='-SUPPORT-'),
         sg.Checkbox('Resistance levels', default=False, key='-RESISTANCE-')],
    ]

    window = sg.Window('Investment Helper', layout, resizable=True)
    window.Finalize()
    window.Maximize()

    while True:
        event, values = window.read()
        print(event, values)
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        if event == 'Normal plot':
            #  MATPLOTLIB
            fig = create_plot(financial_data, values)
            draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['-TOOLBOX-'].TKCanvas)
        if event == 'Candlestick plot':
            # CANDLESTICK PLOT
            fig = create_candlestick_plot(financial_data, values)
            draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['-TOOLBOX-'].TKCanvas)

    window.close()


def create_plot(financial_data, values):
    plt.close('all')
    style.use('seaborn-darkgrid')
    fig = plt.figure(1)
    dpi = fig.get_dpi()

    formatter = get_formatter(values['-PERIOD-'][0])

    ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=4, colspan=1)
    ax2 = plt.subplot2grid((6, 1), (5, 0), rowspan=1, colspan=1, sharex=ax1)

    fig.set_size_inches(404 * 2 / float(dpi), 404 / float(dpi))
    ticker = financial_data.get_ticker_from_readable_stock(values['-STOCK-'][0])

    df = financial_data.get_stock_history_based_on_period(ticker, values['-PERIOD-'][0])
    close_price = df['Close']
    volume = df['Volume']

    ax1.plot_date(close_price.index, close_price.values, '-', linewidth=2)
    ax2.plot_date(volume.index, volume.values, '-', linewidth=0.8)
    ax2.xaxis.set_major_formatter(formatter)
    for label in ax2.xaxis.get_ticklabels():
        label.set_rotation(45)
    ax2.fill_between(volume.index, volume)

    # Moving average:
    if values['-PERIOD-'][0] != '1d' and values['-PERIOD-'][0] != '5d' \
            and values['-PERIOD-'][0] != '1m':  # moving average not available for period 1d, 5d and 1mo.

        if values['-50DMOVAVE-']:  # 50 days moving average
            if values['-PERIOD-'][0] != 'max':
                # to get the startdate for the mov ave calculation
                # and get the df back to that date.
                startdate = get_date_from_period(values['-PERIOD-'][0], 50)
                df = financial_data.get_stock_history_based_on_dates(ticker, startdate, datetime.date.today())
                close_price_mov_ave = df['Close']
            else:
                # if period = max the moving average calculation starts at the first trade day.
                close_price_mov_ave = close_price

            rolling_mean_50 = close_price_mov_ave.rolling(window=50).mean()
            ax1.plot(rolling_mean_50, label='50 days moving average', linewidth=0.8)
            ax1.legend(loc='best', fontsize='small')

        if values['-200DMOVAVE-']:  # 200 days moving average
            if values['-PERIOD-'][0] != 'max':
                # to get the startdate for the mov ave calculation
                # and get the df back to that date.
                startdate = get_date_from_period(values['-PERIOD-'][0], 200)
                df = financial_data.get_stock_history_based_on_dates(ticker, startdate, datetime.date.today())
                close_price_mov_ave = df['Close']
            else:
                # if period = max the moving average calculation starts at the first trade day.
                close_price_mov_ave = close_price

            rolling_mean_200 = close_price_mov_ave.rolling(window=200).mean()
            ax1.plot(rolling_mean_200, label='200 days moving average', linewidth=0.8)
            ax1.legend(loc='best', fontsize='small')

    # Resistance and support levels:
    technical_analysis_object = TechnicalAnalysis(ticker)

    if values['-RESISTANCE-'] and values['-PERIOD-'][0] != '1d' :
        technical_analysis_object.find_resistance_levels(df, resistance_threshold=0.01)
        resistance_df = technical_analysis_object.get_closest_resistance_levels()
        for date in resistance_df.index:
            ax1.hlines(resistance_df.loc[date, 'High'], date, datetime.date.today(), colors='red', linewidths=0.5)


    ax1.set_ylabel('Close Price [$]')
    ax1.set_title(ticker)
    ax2.set_ylabel('Volume [# trades]')

    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.subplots_adjust(left=0.125, bottom=0.171, right=0.9, top=0.88, wspace=0.2, hspace=0.195)

    return fig


def create_candlestick_plot(financial_data, values):
    plt.close('all')
    ticker = financial_data.get_ticker_from_readable_stock(values['-STOCK-'][0])
    df = financial_data.get_stock_history_based_on_period(ticker, values['-PERIOD-'][0])
    #  df = [['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    mov_ave = []
    legend_text = []
    alines_list = []

    # Resistance and support levels:
    technical_analysis_object = TechnicalAnalysis(ticker)

    if values['-50DMOVAVE-'] and values['-200DMOVAVE-']:
        mov_ave.extend([50, 200])
        legend_text.extend(['50 days mov ave', '200 days mov ave'])
    elif values['-50DMOVAVE-']:
        mov_ave.append(50)
        legend_text.append('50 days mov ave')
    elif values['-200DMOVAVE-']:
        mov_ave.append(200)
        legend_text.append('200 days mov ave')

    if values['-RESISTANCE-'] and values['-PERIOD-'][0] != '1d':
        technical_analysis_object.find_resistance_levels(df, resistance_threshold=0.01)
        resistance_df = technical_analysis_object.get_closest_resistance_levels()
        latest_trading_day = df.index[-1]
        for date in resistance_df.index:
            alines_list.append([(date, resistance_df.loc[date, 'High']), (latest_trading_day, resistance_df.loc[date, 'High'])])

    fig, axlist = mpf.plot(df, type='candle', figratio=(9, 6), returnfig=True, volume=True,
                           ylabel='Open, High, Low, Close', style='yahoo', mav=mov_ave,
                           alines=dict(alines=alines_list, colors='red', linewidths=0.5))
    axlist[0].legend(legend_text, loc='best', fontsize='small')
    axlist[0].set_title(ticker)

    return fig


def get_formatter(period):
    if period == '1d':
        return DateFormatter('%H-%M')
    elif period == 'ytd':
        return DateFormatter('%b-%d')
    else:
        return DateFormatter('%Y-%b-%d')
