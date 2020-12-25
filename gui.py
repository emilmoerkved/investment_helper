import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, FigureCanvasAgg, NavigationToolbar2Tk
import matplotlib.ticker as mticker
import mplfinance as mpf



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
    #sg.theme('dark blue')
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
        if event is 'Normal plot':
            #  MATPLOTLIB
            fig = create_plot(financial_data, values)
            draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['-TOOLBOX-'].TKCanvas)
        if event is 'Candlestick plot':
            fig = create_candlestick_plot(financial_data, values)
            draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['-TOOLBOX-'].TKCanvas)
            # CANDLESTICK PLOT

    window.close()


def create_plot(financial_data, values):
    plt.close('all')
    plt.figure(1)
    fig = plt.gcf()
    dpi = fig.get_dpi()

    fig.set_size_inches(404 * 2 / float(dpi), 404 / float(dpi))
    ticker = financial_data.get_ticker_from_readable_stock(values['-STOCK-'][0])
    df = financial_data.get_stock_history(ticker, values['-PERIOD-'][0])
    open_price = df['Open']
    plt.plot(open_price, label=values['-STOCK-'][0])

    # Moving average:
    if not values['-PERIOD-'][0] == '1d' and not values['-PERIOD-'][0] == '5d' \
            and not values['-PERIOD-'][0] == '1m':  # moving average not available for period 1d, 5d and 1m.
        if values['-50DMOVAVE-'] is True:
            rolling_mean_50 = open_price.rolling(window=50).mean()
            plt.plot(rolling_mean_50, label='50 days moving average')
        if values['-200DMOVAVE-'] is True:
            rolling_mean_200 = open_price.rolling(window=200).mean()
            plt.plot(rolling_mean_200, label='200 days moving average')

    plt.grid()
    plt.legend(loc='best', fontsize='small')
    plt.ylabel('Price [$]')

    return fig

def create_candlestick_plot(financial_data, values):
    plt.close('all')
    ticker = financial_data.get_ticker_from_readable_stock(values['-STOCK-'][0])
    df = financial_data.get_stock_history(ticker, values['-PERIOD-'][0])
    ohlc = df[['Open', 'High', 'Low', 'Close']]

    fig, axlist = mpf.plot(ohlc, type='candlestick', no_xgaps=True,  figratio=(8, 5), returnfig=True)

    return fig

