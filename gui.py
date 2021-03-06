# External modules:
import PySimpleGUI as sg

# Internal modules:
from extract_financial_data import FinancialAssetList
from canvas import Canvas
from user_input import UserInput


class Gui:

    def __init__(self):
        self._event = None
        self._values = None
        self._technical_analysis_object = None
        self._financial_asset_list_object = FinancialAssetList()
        self._financial_data_object = None
        self._canvas_object = Canvas()
        self._user_input = UserInput()
        self._layout = None
        self._window = None
        self._period = None
        self._initialize_gui_layout()
        self._initialize_gui_window()

    def _initialize_gui_layout(self):
        self._layout = [
            [sg.Listbox(values=self._financial_asset_list_object.readable_stock_list, size=(40, 50), key='-STOCK-'),
             sg.VSeparator(), sg.Column(
                layout=[[sg.Canvas(key='fig_cv', size=(400 * 3, 400 * 2))]],
                background_color='#DAE0E6',
                pad=(0, 0)),
             sg.Listbox(values=['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'],
                        default_values='ytd', size=(5, 11), key='-PERIOD-')],

            [sg.Canvas(key='-TOOLBOX-', pad=((350, 3), 0))],

            [sg.Button('Normal plot'), sg.Button('Candlestick plot'), sg.Button('Exit'),
             sg.Checkbox('50 days moving average', default=False, key='-50DMVA-', pad=((300, 3,), 0)),
             sg.Checkbox('200 days moving average', default=False, key='-200DMVA-'),
             sg.Checkbox('Support levels', default=False, key='-SUPPORT-'),
             sg.Checkbox('Resistance levels', default=False, key='-RESISTANCE-')],
        ]

    def _initialize_gui_window(self):
        self._window = sg.Window('Investment Helper', self._layout, resizable=True)
        self._window.Finalize()
        self._window.Maximize()

    def start(self):
        while True:
            event, values = self._window.read()
            print('event: ', event)
            print('values: ', values)
            self._user_input.set_event(event)
            self._user_input.set_values(values)

            if self._user_input.event in (sg.WIN_CLOSED, 'Exit'):
                break

            if self._user_input.is_event_plotting():
                self._canvas_object.set_user_input(self._user_input)
                if not self._user_input.is_stock_chosen():
                    sg.popup('You need to choose a stock before plotting!')
                else:
                    self._canvas_object.draw_canvas(canvas_fig=self._window['fig_cv'],
                                                    canvas_toolbox=self._window['-TOOLBOX-'])
        self._window.close()


