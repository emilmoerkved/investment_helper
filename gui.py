import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, FigureCanvasAgg, NavigationToolbar2Tk
import matplotlib.ticker as mticker
import mplfinance as mpf
import datetime
from extract_financial_data import get_date_from_period


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
        [sg.Listbox(values=financial_data.readable_stock_list, size=(40, 25), key='-STOCK-'),
         sg.VSeparator(), sg.Column(
            layout=[[sg.Canvas(key='fig_cv', size=(400 * 2, 400))]],
            background_color='#DAE0E6',
            pad=(0, 0)),
         sg.Listbox(values=period_def, default_values='ytd', size=(5, 11),  key='-PERIOD-')],

        [sg.Canvas(key='-TOOLBOX-', pad=((300, 3), 0))],

        [sg.Button('Normal plot'), sg.Button('Candlestick plot'), sg.Button('Exit'),
         sg.Checkbox('50 days moving average', default=False, key='-50DMOVAVE-', pad=((300, 3,), 0)),
         sg.Checkbox('200 days moving average', default=False, key='-200DMOVAVE-')], ]

    window = sg.Window('Investment Helper', layout)
    window.Finalize()

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
    plt.figure(1)
    fig = plt.gcf()
    dpi = fig.get_dpi()

    fig.set_size_inches(404 * 2 / float(dpi), 404 / float(dpi))
    ticker = financial_data.get_ticker_from_readable_stock(values['-STOCK-'][0])

    df = financial_data.get_stock_history_based_on_period(ticker, values['-PERIOD-'][0])
    close_price = df['Close']
    plt.plot(close_price, label=values['-STOCK-'][0])

    # Moving average:
    if not values['-PERIOD-'][0] == '1d' and not values['-PERIOD-'][0] == '5d' \
            and not values['-PERIOD-'][0] == '1m':  # moving average not available for period 1d, 5d and 1mo.

        if values['-50DMOVAVE-']:  # 50 days moving average
            if not values['-PERIOD-'][0] == 'max':
                # to get the startdate for the mov ave calculation
                # and get the df back to that date.
                startdate = get_date_from_period(values['-PERIOD-'][0], 50)
                df = financial_data.get_stock_history_based_on_dates(ticker, startdate, datetime.date.today())
                close_price_mov_ave = df['Close']
            else:
                # if period = max the moving average calculation starts at the first trade day.
                close_price_mov_ave = close_price

            rolling_mean_50 = close_price_mov_ave.rolling(window=50).mean()
            plt.plot(rolling_mean_50, label='50 days moving average')

        if values['-200DMOVAVE-']:  # 200 days moving average
            if not values['-PERIOD-'][0] == 'max':
                # to get the startdate for the mov ave calculation
                # and get the df back to that date.
                startdate = get_date_from_period(values['-PERIOD-'][0], 200)
                df = financial_data.get_stock_history_based_on_dates(ticker, startdate, datetime.date.today())
                close_price_mov_ave = df['Close']
            else:
                # if period = max the moving average calculation starts at the first trade day.
                close_price_mov_ave = close_price

            rolling_mean_200 = close_price_mov_ave.rolling(window=200).mean()
            plt.plot(rolling_mean_200, label='200 days moving average')

    plt.grid()
    plt.legend(loc='best', fontsize='small')
    plt.ylabel('Close Price [$]')

    return fig


def create_candlestick_plot(financial_data, values):
    plt.close('all')
    ticker = financial_data.get_ticker_from_readable_stock(values['-STOCK-'][0])
    df = financial_data.get_stock_history_based_on_period(ticker, values['-PERIOD-'][0])
    ohlc = df[['Open', 'High', 'Low', 'Close']]

    fig, axlist = mpf.plot(ohlc, type='candlestick', no_xgaps=True,  figratio=(8, 5), returnfig=True)

    return fig


