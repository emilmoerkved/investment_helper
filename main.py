import datetime
import pandas as pd
import numpy as np
import re

from decision_maker import Decision
from extract_financial_data import FinancialData
from helping_file import *
from plotting import Plotting
from User_Specific import UserSpecific

import csv

import matplotlib
import matplotlib.animation as animation
matplotlib.use('TkAgg')
from matplotlib import style
style.use('ggplot')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

import tkinter as tk
from tkinter import ttk, ANCHOR, ACTIVE, filedialog, END, Canvas, NW, DISABLED, Toplevel

from PIL import ImageTk, Image

LARGE_FONT = ('Verdana', 12)
NORM_FONT = ('Verdana', 10)
SMALL_FONT = ('Verdana', 8)

f = plt.figure()
a = f.add_subplot(111)

financial_data = FinancialData()
DatCounter = 9000
DataPace = 'ytd'
candleWidth = 0.008
paneCount = 1
topIndicator = 'none'
bottomIndicator = 'none'
mainIndicator = 'none'
chartLoad = True
EME = []
SMA = []
ticker = '^GSPC'  # not needed?
draw_figure = True  # Not needed?
cont_ave = False
global img
global slider

user_specific_object = UserSpecific()
general_config_object = GeneralConfig()
main_page_config_oject = MainPageConfig()
start_page_config_object = StartPageConfig()

def loadChart(run):
    global chartLoad

    if run == 'start':
        chartLoad = True
    elif run == 'stop':
        chartLoad = False


# Defines the help section with tutorial of the application
def tutorial():

    def page2():
        tut.destroy()
        tut2 = tk.Tk()

        def page3():
            tut2.destroy()
            tut3 = tk.Tk()

            tut3.wm_title('Part 3!')
            label = ttk.Label(tut3, text='Part 3', font=NORM_FONT)
            label.pack(side='top', fill='x', pady=10)
            B1 = ttk.Button(tut3, text='Done!', command=tut3.destroy)
            B1.pack()
            tut3.mainloop()

        tut2.wm_title('Part 2!')
        label = ttk.Label(tut2, text='Part 2', font=NORM_FONT)
        label.pack(side='top', fill='x', pady=10)
        B1 = ttk.Button(tut2, text='Done!', command=page3)
        B1.pack()
        tut2.mainloop()

    tut = tk.Tk()
    tut.wm_title('Tutorial')
    label = ttk.Label(tut, text='What do you need help with?', font=NORM_FONT)
    label.pack(side='top', fill='x', pady=10)

    B1 = ttk.Button(tut, text='Overview of the application', command=page2)
    B1.pack()
    B2 = ttk.Button(tut, text='How do I trade with this client', command=lambda: popupmsg('Not yet completed!'))
    B2.pack()
    B3 = ttk.Button(tut, text='Indicator Questions/Help', command=lambda: popupmsg('Not yet completed!'))
    B3.pack()

    tut.mainloop()


def tech_analysis_window():
    tech_analysis = tk.Tk()
    tech_analysis.geometry('420x380')
    tech_analysis.wm_title('Technical Analysis Settings')

    def s_moving_average():
        input_window('How many days?', function='simple moving average')
        update_listbox()

    def e_moving_average():
        input_window('How many days?', function='exponential moving average')
        update_listbox()

    def rsi():
        input_window('How many days?', function='relative strength index')
        update_listbox()

    def bollinger_band():
        input_window('How many days?', function='bollinger bands')
        update_listbox()

    def update_listbox():
        lb_tech_functions.delete(0, tk.END)
        for i, s in enumerate(user_specific_object.tech_analysis_string().split('\n')):
            lb_tech_functions.insert(i, s)

    def remove():
        lb_string = user_specific_object.tech_analysis_string()
        list_lb = lb_string.split('\n')
        last_function = ''
        for i, string in enumerate(list_lb):
            if string in user_specific_object.functions.keys():
                last_function = string
                if i in lb_tech_functions.curselection():
                    user_specific_object.clear_function(last_function)
            else:
                if i in lb_tech_functions.curselection():
                    digit_pattern = re.compile(r'\d+')
                    digit = re.search(digit_pattern, string).group(0)  # type string
                    user_specific_object.remove_from_function(int(digit), function=last_function)
        update_listbox()

    def execute():
        plotting_obj.add_to_main_figure(user_specific_object.functions)
        ticker = plotting_obj.user_specific_obj.get_shortlist()[next(iter(user_specific_object.get_shortlist()))]
        plotting_obj.set_ticker(ticker)
        plotting_obj.cmd_draw_figure(ticker)  # problem that last figure gets cleared...

    def input_window(label_str, function=''):

        input_wnd = Toplevel(tech_analysis)

        def confirm():
            days = entry.get()  # type string
            if days.isnumeric() is False:
                input_wnd.destroy()
                popupmsg('Input has to be numeric!')
            else:
                user_specific_object.append_to_function(int(days), function=function)
            input_wnd.destroy()



        label = ttk.Label(input_wnd, text=label_str)
        entry = ttk.Entry(input_wnd)
        b_confirm = ttk.Button(input_wnd, text='Confirm', command=confirm)
        b_cancel = ttk.Button(input_wnd, text='Cancel', command=input_wnd.destroy)

        label.pack()
        entry.pack()
        b_confirm.pack()
        b_cancel.pack()

        input_wnd.grab_set()
        tech_analysis.wait_window(input_wnd)


    lb_tech_functions = tk.Listbox(tech_analysis, height=15, width=25, selectmode='extended')
    lb_tech_functions.place(relx=0.6, rely=0.15)

    exec_button = ttk.Button(tech_analysis, text='Execute', command=execute)
    remove_button = ttk.Button(tech_analysis, text='Remove', command=remove)
    exec_button.place(relx=0.8, rely=0.9)
    remove_button.place(relx=0.6, rely=0.9)

    mb_tech_func = ttk.Menubutton(tech_analysis, text='technical function')
    m_tech_func = tk.Menu(mb_tech_func)
    m_tech_func.add_command(label='Standard Moving Average', command=s_moving_average)
    m_tech_func.add_command(label='Exponential Moving Average', command=e_moving_average)
    m_tech_func.add_command(label='RSI', command=rsi)
    m_tech_func.add_command(label='Bollinger Bands', command=bollinger_band)
    mb_tech_func.place(relx=0.05, rely=0.3)
    mb_tech_func["menu"] = m_tech_func

    tech_analysis.mainloop()


def create_shortlist():
    header = ['Company', 'Ticker', 'Country']
    new_shortlist_df = pd.DataFrame(columns=header)

    def attach_to_shortlist(company):
        for i in lb1.curselection():
            company = lb1.get(i)
            if company not in new_shortlist_df['Company']:
                # df_new_row = pd.DataFrame([[company, financial_data.asset_dictionary[company], financial_data.country]],
                #                          columns=header)
                new_shortlist_df.loc[new_shortlist_df.shape[0]] = [company,
                                                                       financial_data.asset_dictionary[company],
                                                                       financial_data.country]
                print(new_shortlist_df)
                lb2.insert(len(new_shortlist_df)-1, company)

    def detach_from_shortlist(company):
        #print(lb2.get(0, tk.END).index(stock))
        idx = new_shortlist_df[new_shortlist_df['Company']==company].index.values
        new_shortlist_df.drop(idx, inplace=True)
        lb2.delete(lb2.get(0, tk.END).index(company))

    sl = tk.Tk()
    sl.geometry('520x480')
    sl.wm_title('Create shortlist')

    label1 = ttk.Label(sl, text='Search in market:', font=NORM_FONT)
    label1.place(relx=0.02, rely=0.02)

    def filter_lb(event):
        lb1.delete(0, END)
        i = 0
        for company in financial_data.companylist:
            if search.get().capitalize() in company.capitalize():
                lb1.insert(i, company)
                i += 1

    search = ttk.Entry(sl)
    search.place(relx=0.02, rely=0.08)
    search.bind('<Return>', filter_lb)

    lb1 = tk.Listbox(sl, height=15, width=25, selectmode='extended')
    lb1.place(relx=0.01, rely=0.15)
    scrollbar1 = tk.Scrollbar(sl)

    for i, company in enumerate(financial_data.companylist):
        lb1.insert(i, company)
    lb1.config(yscrollcommand=scrollbar1.set)
    scrollbar1.config(command=lb1.yview)

    lb2 = tk.Listbox(sl, height=15, width=25)
    lb2.place(relx=0.6, rely=0.15)
    for i, company in enumerate(new_shortlist_df['Company']):
        lb2.insert(i, company)

    def change_marketplace(marketplace, country):
        financial_data.change_marketlist(marketplace, country)
        sl.destroy()
        create_shortlist()

    menu_button = ttk.Menubutton(sl, text='marketplace')
    menu = tk.Menu(menu_button)
    menu.add_command(label='S&P 500 - USA', command=lambda: change_marketplace('S&P 500', 'USA'))
    menu.add_command(label='Oslo Stock Exchange - NOR', command=lambda: change_marketplace('Oslo Stock Exchange', 'NOR'))
    menu.add_command(label='Nasdaq Stockholm - SWE', command=lambda: change_marketplace('Nasdaq Stockholm', 'SWE'))
    menu.add_command(label='Railway Shares - World', command=lambda: change_marketplace('Railway', 'WORLD'))
    menu.add_command(label='Indexes and Other - WORLD', command=lambda: change_marketplace('Indexes and Other', 'WORLD'))
    menu_button.place(relx=0.35, rely=0.15)
    menu_button["menu"] = menu

    label2 = ttk.Label(sl, text=financial_data.market)
    label2.place(relx=0.35, rely=0.25)
    label3 = ttk.Label(sl, text=financial_data.country)
    label3.place(relx=0.35, rely=0.29)

    B1 = ttk.Button(sl, text='Add to shortlist', command=lambda: attach_to_shortlist(lb1.get(ACTIVE)))
    B1.place(relx=0.01, rely=0.7)
    B2 = ttk.Button(sl, text='Remove from shortlist', command=lambda: detach_from_shortlist(lb2.get(ACTIVE)))
    B2.place(relx=0.5, rely=0.7)
    B3 = ttk.Button(sl, text='Save shortlist', command=lambda: write_shortlist_to_textfile(entry2.get(),
                                                                                           new_shortlist_df))
    B3.place(relx=0.01, rely=0.9)
    B4 = ttk.Button(sl, text='Exit', command=sl.destroy)
    B4.place(relx=0.5, rely=0.9)

    label2 = ttk.Label(sl, text='Name of shortlist:')
    label2.place(relx=0.01, rely=0.8)

    entry2 = ttk.Entry(sl)
    entry2.place(relx=0.5, rely=0.8)
    sl.mainloop()


def open_file_dialog():
    file = filedialog.askopenfilename(initialdir=r'C:\Users\Emil\PycharmProjects\tkinter_tutorial\Shortlists')
    print(file)
    if file:
        # Take data from .csv file for new shortlist
        shortlist = create_new_shortlist(file) # shortlist of type dict
        print(shortlist)
        # Set shortlist
        user_specific_object.set_shortlist(shortlist)


def create_new_shortlist(file):
    df = pd.read_csv(file)
    return dict(df[['Company', 'Ticker']].values)


def write_shortlist_to_textfile(name, new_shortlist_df):
    folder = r'C:\Users\Emil\PycharmProjects\tkinter_tutorial\Shortlists'
    filepath = '\\'.join([folder, name])+'.txt'
    new_shortlist_df.to_csv(filepath, index=False)


def changeTimeFrame(tf):
    global DataPace
    global DatCounter
    if tf == '7d' and resampleSize == '1Min':
        popupmsg("Too much data chosen, choose a smaller time framer or higher OHLC interval")
    else:
        DataPace = tf
        DatCounter = 9000


def changeSampleSize(size, width):
    global resampleSize
    global DatCounter
    global candleWidth
    if DataPace == '7d' and resampleSize == '1Min':
        popupmsg("Too much data chosen, choose a smaller time framer or higher OHLC interval")
    elif DataPace == 'tick':
        popupmsg('You\'re currently viewing tick data, not OHLC.')
    else:
        resampleSize = size
        DatCounter = 9000
        candleWidth = width


def popupmsg(msg):
    popup = tk.Tk()

    popup.wm_title("!")
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Okay", command=popup.destroy)
    B1.pack()
    popup.mainloop()


def info_window():
    iw = tk.Tk()

    tb = tk.Text(iw, height=20)
    financial_entity_info = financial_data.get_stock_info(ticker)  # ticker from global workspace
    print(ticker)
    for i, key in enumerate(financial_entity_info):
        tb.insert('end', key+': '+5*'\t'+str(financial_entity_info[key])+'\n')
    tb.pack()


def correlation_matrix():

    # create window to show correlation
    corr_window = tk.Tk()
    corr_window.geometry('1040x480')
    corr_window.wm_title('Correlation analysis')

    fig = plotting_obj.get_correlation_fig()
    canvas = FigureCanvasTkAgg(fig, corr_window)

    period = '10y'

    def plot_correlation():
        nonlocal canvas
        plotting_obj.correlation_matrix(fig, period)
        canvas.draw()
        canvas.get_tk_widget().place(relx=relx_canvas, rely=rely_canvas)

    def plot_cross_correlation(asset1, asset2):
        pb.place(relx=relx_pb, rely=rely_pb)  # show progress bar
        pb.start()  # start progress bar
        ticker1 = plotting_obj.user_specific_obj.get_shortlist()[asset1]
        ticker2 = plotting_obj.user_specific_obj.get_shortlist()[asset2]

        nonlocal canvas
        plotting_obj.cross_correlation(fig, ticker1, ticker2, pb, corr_window)
        pb.stop()  # stop progress bar
        pb.place_forget()  # hide progress bar
        canvas.draw()
        canvas.get_tk_widget().place(relx=relx_canvas, rely=rely_canvas)

    def filter_correlation(period, x):
        nonlocal canvas
        plotting_obj.correlation_matrix(fig, period, x)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def change_period(per):
        nonlocal period
        menu_button.configure(text=per)
        period = per

    # Creation of widgets:
    corr_button = ttk.Button(corr_window, text='Plot correlation matrix of shortlist', command=plot_correlation)
    filter_button = ttk.Button(corr_window, text='Filter', command=lambda: filter_correlation(period, entry_x.get()))

    cross_corr_button = ttk.Button(corr_window, text='Calculate cross correlation of asset1 and asset2',
                                   command=lambda: plot_cross_correlation(lb_ticker1.get(ACTIVE),
                                                                          lb_ticker2.get(ACTIVE)))

    # Progress bar
    pb = ttk.Progressbar(corr_window, orient=tk.HORIZONTAL, length=100, mode='determinate')

    # Menu for time of analysis
    menu_button = ttk.Menubutton(corr_window, text='10y')
    menu = tk.Menu(menu_button)
    # before python 3.6 the dictionary is not ordered, hence you might see a strange order of periods in the menu
    for key, val in financial_data.get_yfinance_periods().items():
        menu.add_command(label=key, command=lambda v=val: change_period(v))  # v=val for binding issue with lambda

    # listboxes:
    lb_ticker1 = tk.Listbox(corr_window, height=min(20, len(user_specific_object.get_shortlist())), selectmode='browse',
                            exportselection=0)
    lb_ticker2 = tk.Listbox(corr_window, height=min(20, len(user_specific_object.get_shortlist())), selectmode='browse',
                            exportselection=0)
    for i, asset in enumerate(user_specific_object.get_shortlist()):
        lb_ticker1.insert(i, asset)
        lb_ticker2.insert(i, asset)

    # filter entry:
    entry_x = ttk.Entry(corr_window, text='filter value', width=5)

    # labels:
    asset1_label = tk.Label(corr_window, text='Asset 1:', font=LARGE_FONT)
    asset2_label = tk.Label(corr_window, text='Asset 2:', font=LARGE_FONT)
    period_label = tk.Label(corr_window, text='Time of analysis:', font=NORM_FONT)


    # calculating position of widgets:
    length_sl = len(user_specific_object.get_shortlist())
    buffer = 0.02
    rely_label = buffer
    relx_label1 = 0.01
    relx_label2 = 0.16
    l_per_asset = 0.033
    rely_shortlist = rely_label + 0.03 + buffer
    button = 0.04
    rely_cross_corr = rely_shortlist+min(0.6, length_sl*l_per_asset)+buffer
    cross_corr_button.place(relx=0.5, rely=rely_cross_corr)
    rely_plot_corr = rely_cross_corr+button+buffer
    rely_filter = rely_plot_corr+button+buffer
    rely_menubutton = rely_filter+button+buffer
    rely_period_label = rely_menubutton
    relx_period_label = 0.38
    rely_canvas = 0.01
    relx_canvas = 0.3
    relx_pb = relx_canvas+(1-relx_canvas)/2
    rely_pb = rely_canvas+(1-rely_canvas)/2

    # Placement of widgets:
    asset1_label.place(relx=relx_label1, rely=rely_label)
    asset2_label.place(relx=relx_label2, rely=rely_label)
    lb_ticker1.place(relx=0.01, rely=rely_shortlist)
    lb_ticker2.place(relx=0.16, rely=rely_shortlist)
    corr_button.place(relx=0.5, rely=rely_plot_corr)
    entry_x.place(relx=0.5, rely=rely_filter)
    filter_button.place(relx=0.55, rely=rely_filter)
    period_label.place(relx=relx_period_label, rely=rely_period_label)
    menu_button.place(relx=0.5, rely=rely_menubutton)
    menu_button["menu"] = menu

    corr_window.mainloop()


def calculate_std():

    canvas = FigureCanvasTkAgg()

    def plot_std(years=5):
        nonlocal canvas
        canvas = FigureCanvasTkAgg(plotting_obj.plot_std(years), std_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

    std_window = tk.Tk()

    calc_std_button = ttk.Button(std_window,
                                 text='Calculate standard deviation and average rate of return of shortlist',
                                 command=lambda: plot_std(years=analysis_period_lb.get(ACTIVE)))
    calc_std_button.pack()

    analysis_period_label = ttk.Label(std_window, text='Based on: [years]', font=NORM_FONT)
    analysis_period_lb = tk.Listbox(std_window, height=min(20, len(user_specific_object.get_shortlist())),
                                    selectmode='browse')
    for i, key in enumerate([5, 10]):
        analysis_period_lb.insert(i, key)
    analysis_period_label.pack()
    analysis_period_lb.pack()

    canvas.draw()
    canvas.get_tk_widget().pack(side='top', fill='both', expand=True)

    std_window.mainloop()


class PersonalFinancialDashboardApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)

        tk.Tk.iconbitmap(self, 'PerfCenterCpl.ico')
        tk.Tk.wm_title(self, "Personal Financial Dashboard")

        self.container = tk.Frame(self)
        self.container.pack(side='top', fill='both', expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self._create_menu()

        tk.Tk.config(self, menu=self.menubar)

        self.frames = {}
        for F in (MainPage, StartPage):
            frame = F(self.container, self)  # initialize page classes
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')
        self.show_frame(StartPage)

        # self.add_in_windows = {}
        # for W in [BackTesting]:
        #     window = W()
        #     self.add_in_windows[W] = window

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def show_window(self, window):
        win = self.add_in_windows[window]
        win.show_window()

    def open_shortlist(self):
        # Choose shortlist to open
        open_file_dialog()
        # destroy Main Page window
        self.frames[MainPage].destroy()

        #Change ticker and draw figure
        ticker = plotting_obj.user_specific_obj.get_shortlist()[next(iter(user_specific_object.get_shortlist()))]
        plotting_obj.set_ticker(ticker)
        plotting_obj.cmd_draw_figure(ticker)

        # create new Main Page Window
        frame = MainPage(self.container, self)
        self.frames[MainPage] = frame
        frame.grid(row=0, column=0, sticky='nsew')
        # Show Main Page window
        self.show_frame(MainPage)

    def _create_menu(self):
        self.menubar = tk.Menu(self.container)
        self._create_filemenu()
        self._create_shortlistmenu()
        self._create_plot_menu()
        self._create_analysis_menu()
        self._create_backtesting_menu()
        self._create_helpmenu()

    def _create_filemenu(self):
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label='Save settings', command=lambda: popupmsg("not supported just yet"))
        self.filemenu.add_separator()
        self.filemenu.add_command(label='Exit', command=quit)
        self.menubar.add_cascade(label='File', menu=self.filemenu)

    def _create_shortlistmenu(self):
        self.shortlist_menu = tk.Menu(self.menubar, tearoff=1)
        self.shortlist_menu.add_command(label='Create shortlist', command=create_shortlist)
        self.shortlist_menu.add_command(label='Open shortlist', command=self.open_shortlist)
        self.menubar.add_cascade(label='Shortlist', menu=self.shortlist_menu)

    def _create_plot_menu(self):
        self.plot_menu = tk.Menu(self.menubar, tearoff=1)
        self.sub_plot_menu = tk.Menu(self.plot_menu, tearoff=0)
        for i in range(1, 6):
            self.sub_plot_menu.add_command(label=str(i), command=lambda i=i: self.configure_main_page(plot=i))
        self.menubar.add_cascade(label='Plots', menu=self.plot_menu)
        self.plot_menu.add_cascade(label='Plots', menu=self.sub_plot_menu)

    def _create_analysis_menu(self):
        self.analysis_menu = tk.Menu(self.menubar, tearoff=1)
        self.analysis_menu.add_command(label='Technical Analysis Filter', command=tech_analysis_window)
        self.analysis_menu.add_command(label='Correlation matrix', command=correlation_matrix)
        self.analysis_menu.add_command(label='Standard deviation', command=calculate_std)
        self.menubar.add_cascade(label='Analysis', menu=self.analysis_menu)

    def _create_backtesting_menu(self):
        self.backtesting_menu = tk.Menu(self.menubar, tearoff=1)
        self.backtesting_menu.add_command(label='Set up backtesting', command=lambda: BackTesting())
        self.menubar.add_cascade(label='Backtesting', menu=self.backtesting_menu)

    def _create_helpmenu(self):
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label='Tutorial', command=tutorial)
        self.menubar.add_cascade(label='Help', menu=self.helpmenu)

    def configure_main_page(self, plot=1):
        if plot > user_specific_object.plot_number:
            for i in range(plot-user_specific_object.plot_number):
                prev_ticker = plotting_obj.ticker[-1]
                plotting_obj.append_ticker(prev_ticker)
                plotting_obj.append_period('ytd')
        elif plot < user_specific_object.plot_number:
            for i in range(user_specific_object.plot_number-plot):
                plotting_obj.ticker.pop(-1)
                plotting_obj.period.pop(-1)
        user_specific_object.set_plot_number(plot)
        plotting_obj.cmd_draw_figure()
        self.frames[MainPage].destroy()
        # create new Main Page Window
        frame = MainPage(self.container, self)
        self.frames[MainPage] = frame
        frame.grid(row=0, column=0, sticky='nsew')
        # Show Main Page window
        self.show_frame(MainPage)


class StartPage(tk.Frame):

    def __init__(self, parent, controller):  # parent = container, controller = PersonalFinancialDashboardapp
        tk.Frame.__init__(self, parent)
        title_label = ttk.Label(self, text=("""Welcome to your Personal Financial Dashboard"""), font=LARGE_FONT)
        title_label.pack(pady=10, padx=10)

        c = Canvas(self, width=720, height=580)
        c.pack()
        file = Image.open("StartPage.jpg")
        img = ImageTk.PhotoImage(file)
        self.img = img  # to prevent img from being garbage collected
        c.create_image(20, 20, anchor=NW, image=img)

        def_shortlist_button = ttk.Button(self, text='Enter with default shortlist',
                                          command=lambda: controller.show_frame(MainPage))
        def_shortlist_button.place(relx=0.8, rely=0.2)

        predef_shortlist_button = ttk.Button(self, text='Enter with predefined shortlist',
                                             command=controller.open_shortlist)
        predef_shortlist_button.place(relx=0.8, rely=0.4)

        leave_button = ttk.Button(self, text='Leave', command=quit)
        leave_button.place(relx=0.8, rely=0.6)


class MainPage(tk.Frame):

    def __init__(self, parent, controller):
        '''
        First create variables of some common configuration variables that is used more than once.
        A next step could be to create a .ini file of this. But should not be a priority for now.
        '''
        canvas_width = 720
        self.canvas_height = 680
        ani_interval = 1000
        self.scrolling_plot_number = 3  # to make it available in other methods
        self.relx_menu_t = 0.65  # relative x position of parent (canvas) for ticker menu
        self.relx_menu_p = 0.75  # relative x position of parent (canvas) for period menu

        # animation.FuncAnimation ensures animate function to update f every interval
        self.ani = animation.FuncAnimation(plotting_obj.f1, plotting_obj.animate, interval=ani_interval)
        self.controller = controller  # To make it available in other methods? Good programming practice?
        tk.Frame.__init__(self, parent)

        title_label = tk.Label(self, text='DASHBOARD', font=LARGE_FONT)
        title_label.place(relx=0.5, rely=0.02)

        self.shortlist_label = ttk.Label(self, text='Shortlist', font=NORM_FONT)
        self.shortlist_label.place(relx=0.02, rely=0.02)
        self.shortlist_lb = tk.Listbox(self, height=min(20, len(user_specific_object.get_shortlist())),
                                       selectmode='browse')
        self._insert_shortlist_to_lb()
        self.shortlist_lb.place(relx=0.02, rely=0.05)

        info_button = ttk.Button(self, text='Info', command=self._show_info_window)
        info_button.place(relx=0.13, rely=0.05)

        financials_button = ttk.Button(self, text='Financials', command=self._show_financials_window)
        financials_button.place(relx=0.13, rely=0.10)

        balance_sheet_button = ttk.Button(self, text='Balance Sheet', command=self._show_balance_sheet_window)
        balance_sheet_button.place(relx=0.13, rely=0.15)

        cash_flow_button = ttk.Button(self, text='Cash Flow', command=self._show_cashflow_window)
        cash_flow_button.place(relx=0.13, rely=0.20)

        earnings_button = ttk.Button(self, text='Earnings', command=self._show_earnings_window)
        earnings_button.place(relx=0.13, rely=0.25)

        dividends_button = ttk.Button(self, text='Dividends', command=self._show_dividens_window)
        dividends_button.place(relx=0.13, rely=0.30)

        shareholders_button = ttk.Button(self, text='Shareholders')
        shareholders_button.place(relx=0.13, rely=0.35)

        calender_button = ttk.Button(self, text='Calender')
        calender_button.place(relx=0.13, rely=0.40)

        self.plot_canvas = FigureCanvasTkAgg(plotting_obj.f1, self)
        self.plot_canvas.get_tk_widget().place(relx=0.4, rely=0.05)
        plots = user_specific_object.plot_number
        if plots < self.scrolling_plot_number:
            self.plot_canvas.get_tk_widget().config(width=canvas_width, height=self.canvas_height)
        elif plots >= self.scrolling_plot_number:
            self.plot_canvas.get_tk_widget().config(width=canvas_width, height=self.canvas_height * plots / 2)
            self.plot_canvas.get_tk_widget().config(scrollregion=(0, 0, canvas_width, self.canvas_height * plots / 1.3))
            self.vbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.plot_canvas.get_tk_widget().yview)
            self.plot_canvas.get_tk_widget().configure(yscrollcommand=self.vbar.set)
            self.plot_canvas.get_tk_widget().bind('<Enter>', self._bound_to_mousewheel)
            self.plot_canvas.get_tk_widget().bind('<Leave>', self._unbound_to_mousewheel)

        self._create_ticker_menu_widget()
        self._create_period_menu_widget()

    def _show_info_window(self):
        iw = tk.Tk()
        ticker = user_specific_object.get_shortlist()[self.shortlist_lb.get(ACTIVE)]

        tb = tk.Text(iw, height=20)
        financial_entity_info = financial_data.get_stock_info(ticker)  # ticker from global workspace
        for i, key in enumerate(financial_entity_info):
            tb.insert('end', key + ': ' + 5 * '\t' + str(financial_entity_info[key]) + '\n')
        tb.pack()

    def _show_financials_window(self):
        fw = tk.Tk()
        ticker = user_specific_object.get_shortlist()[self.shortlist_lb.get(ACTIVE)]
        print(ticker)
        financial_entity_financials = financial_data.get_stock_financials(ticker)
        cols = list(financial_entity_financials.columns.strftime("%m/%d/%Y"))
        cols.insert(0, 'Explanation')

        tree = ttk.Treeview(fw, columns=cols, show='headings')

        for col in cols:
            tree.heading(col, text=col, anchor=tk.CENTER)

        for i, d in enumerate(financial_entity_financials.itertuples()):
            l = []
            for j in d:
                if type(j) is float:
                    try:
                        l.append('{:,}'.format(int(j)))
                    except Exception as e:
                        print(e)
                elif type(j) is int:
                    l.append({'{:,}'.format(j)})
                else:
                    l.append(j)
            t = tuple(l)
            tree.insert('', index=i, values=t)

        tree.pack()

    def _show_balance_sheet_window(self):
        bsw = tk.Tk()
        ticker = user_specific_object.get_shortlist()[self.shortlist_lb.get(ACTIVE)]
        print(ticker)
        financial_entity_balance_sheet = financial_data.get_stock_balance_sheet(ticker)
        cols = list(financial_entity_balance_sheet.columns.strftime("%m/%d/%Y"))
        cols.insert(0, 'Explanation')

        tree = ttk.Treeview(bsw, columns=cols, show='headings')

        for col in cols:
            tree.heading(col, text=col, anchor=tk.CENTER)

        for i, d in enumerate(financial_entity_balance_sheet.itertuples()):
            l = []
            for j in d:
                if type(j) is float:
                    try:
                        l.append('{:,}'.format(int(j)))
                    except Exception as e:
                        print(e)
                elif type(j) is int:
                    l.append({'{:,}'.format(j)})
                else:
                    l.append(j)
            t = tuple(l)
            tree.insert('', index=i, values=t)

        tree.pack()

    def _show_cashflow_window(self):
        bsw = tk.Tk()
        ticker = user_specific_object.get_shortlist()[self.shortlist_lb.get(ACTIVE)]
        print(ticker)
        financial_entity_cashflow = financial_data.get_stock_cashflow(ticker)
        cols = list(financial_entity_cashflow.columns.strftime("%m/%d/%Y"))
        cols.insert(0, 'Explanation')

        tree = ttk.Treeview(bsw, columns=cols, show='headings')

        for col in cols:
            tree.heading(col, text=col, anchor=tk.CENTER)

        for i, d in enumerate(financial_entity_cashflow.itertuples()):
            l = []
            for j in d:
                if type(j) is float:
                    try:
                        l.append('{:,}'.format(int(j)))
                    except Exception as e:
                        print(e)
                elif type(j) is int:
                    l.append({'{:,}'.format(j)})
                else:
                    l.append(j)
            t = tuple(l)
            tree.insert('', index=i, values=t)

        tree.pack()

    def _show_dividens_window(self):
        dw = tk.Tk()
        ticker = user_specific_object.get_shortlist()[self.shortlist_lb.get(ACTIVE)]
        print(ticker)

        financial_entity_dividends = financial_data.get_stock_dividends(ticker)
        cols = ['Date', 'Dividends']

        tree = ttk.Treeview(dw, columns=cols, show='headings')

        for col in cols:
            tree.heading(col, text=col, anchor=tk.CENTER)

        j = 0
        for i, date in reversed(list(enumerate(financial_entity_dividends.index))):
            v = (date, financial_entity_dividends[i])
            tree.insert('', index=j, values=v)
            j += 1

        tree.pack()

    def _show_earnings_window(self):
        w = tk.Tk()

        ticker = user_specific_object.get_shortlist()[self.shortlist_lb.get(ACTIVE)]
        print(ticker)

        financial_entity_earnings = financial_data.get_stock_earnings(ticker)
        cols = list(financial_entity_earnings.columns)
        cols.insert(0, 'Year')

        tree = ttk.Treeview(w, columns=cols, show='headings')
        canvas = FigureCanvasTkAgg(plotting_obj.plot_df(financial_entity_earnings), w)

        for col in cols:
            tree.heading(col, text=col, anchor=tk.CENTER)

        for i, d in enumerate(financial_entity_earnings.itertuples()):
            tree.insert('', index=i, values=d)


        tree.pack()
        canvas.get_tk_widget().pack()

        w.mainloop()

    def _bound_to_mousewheel(self, event):
        self.plot_canvas.get_tk_widget().bind_all('<MouseWheel>', self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.plot_canvas.get_tk_widget().unbind_all('<MouseWheel>')

    def _on_mousewheel(self, event):
        pre_y1 = self.plot_canvas.get_tk_widget().yview()[0]
        self.plot_canvas.get_tk_widget().yview_scroll(int(-1*event.delta/120), "units")  # can be "units" or "pages"
        post_y1 = self.plot_canvas.get_tk_widget().yview()[0]
        rel_scroll_canvas = 2/1.3  # relative size between scroll region and canvas height
        delta_y = (post_y1-pre_y1)*rel_scroll_canvas
        self._adjust_position_on_menus(delta_y)

    def _adjust_position_on_menus(self, delta_y):
        def get_rely_t(i):
            return self.menu_button_ticker[i].winfo_y()/(self.canvas_height*user_specific_object.get_plot_number()/2)

        def get_rely_p(i):
            return self.menu_button_period[i].winfo_y()/(self.canvas_height * user_specific_object.get_plot_number()/2)

        m_t = self.menu_button_ticker
        m_p = self.menu_button_period
        plots = user_specific_object.plot_number
        for i in range(plots):
            m_t[i].place(relx=self.relx_menu_t, rely=get_rely_t(i)-delta_y)
            m_p[i].place(relx=self.relx_menu_p, rely=get_rely_p(i)-delta_y)

    def _create_ticker_menu_widget(self):
        self.menu_button_ticker = [ttk.Menubutton(self.plot_canvas.get_tk_widget(), text='ticker') for i in range(5)]
        menu = [tk.Menu(m) for m in self.menu_button_ticker]

        for name in user_specific_object.get_shortlist():
            for i, m in enumerate(menu, start=1):
                # lambda function needs to bind to name (hence name=name)
                m.add_command(label=name, command=lambda n=name, i=i: self._change_ticker(n, i))

        if user_specific_object.plot_number == 1:
            start_y_pos = 0.08
            increment = -1  # no increment for this case but has a value for common solution
        elif user_specific_object.plot_number == 2:
            start_y_pos = 0.08
            increment = 0.37
        elif user_specific_object.plot_number == 3:
            start_y_pos = 0.092
            increment = 0.247
        elif user_specific_object.plot_number == 4:
            start_y_pos = 0.10
            increment = 0.185
        elif user_specific_object.plot_number == 5:
            start_y_pos = 0.104
            increment = 0.148
        for i in range(user_specific_object.plot_number):
            m = self.menu_button_ticker[i]
            m.place(relx=self.relx_menu_t, rely=start_y_pos + increment * i)
            m["menu"] = menu[i]

    def _create_period_menu_widget(self):
        self.menu_button_period = [ttk.Menubutton(self.plot_canvas.get_tk_widget(), text='period') for i in range(5)]
        menu = [tk.Menu(m) for m in self.menu_button_period]

        # before python 3.6 the dictionary is not ordered, hence you might see a strange order of periods in the menu
        for key, val in financial_data.get_yfinance_periods().items():
            for i, m in enumerate(menu, start=1):
                # lambda function needs to bind to val (hence val=val)
                m.add_command(label=key, command=lambda v=val, i=i: self._change_period(v, i))

        # Dette blir ikke helt rett pga når du åpner ny shortlist vil den tidligere asset fortsatt vises (f.eks. S&P500).
        # Det er ikke meningen period skal forsvinne fra S&P500 men fra Yield curve.
        if 'SPECIAL' not in user_specific_object.get_shortlist()[next(iter(user_specific_object.get_shortlist()))]:
            if user_specific_object.plot_number == 1:
                start_y_pos = 0.08
                increment = -1  # no increment for this case but has a value for common solution
            elif user_specific_object.plot_number == 2:
                start_y_pos = 0.08
                increment = 0.37
            elif user_specific_object.plot_number == 3:
                start_y_pos = 0.092
                increment = 0.247
            elif user_specific_object.plot_number == 4:
                start_y_pos = 0.10
                increment = 0.185
            elif user_specific_object.plot_number == 5:
                start_y_pos = 0.104
                increment = 0.148
            for i in range(user_specific_object.plot_number):
                m = self.menu_button_period[i]
                m.place(relx=self.relx_menu_p, rely=start_y_pos + increment * i)
                m["menu"] = menu[i]

    def _insert_shortlist_to_lb(self):
        for i, key in enumerate(user_specific_object.get_shortlist()):
            self.shortlist_lb.insert(i, key)

    def _change_period(self, period, plot_number=1):
        plotting_obj.set_period(period, plot_number)
        plotting_obj.cmd_draw_figure(period=period)

    def _change_ticker(self, name, plot_number=1):
        ticker = plotting_obj.user_specific_obj.get_shortlist()[name]
        if 'SPECIAL' in ticker:
            self.menu_button_period[plot_number-1].place_forget()
        # Create a condition where you place the period that has been removed earlier
        plotting_obj.set_ticker(ticker, plot_number)
        plotting_obj.cmd_draw_figure(ticker)


class IterableWindow(type):
    def __iter__(cls):
        return iter(cls.__)


class BackTesting():

    def __init__(self):
        self.bt_window = tk.Tk()
        self.bt_window.geometry('480x520')
        self.bt_window.wm_title('Backtesting')

        # default for testing:
        self.buy_cond = '^GSPC.Clp>^GSPC.MvAv(50)'
        self.sell_cond = '^GSPC.Clp<^GSPC.MvAv(Opt_f[51, 200])'
        user_specific_object.set_algorithm(self.buy_cond, self.sell_cond)
        cap_def = '10000'
        com_def = '2'
        per_def = '10 years'

        self.buy_ticker = 'S&P 500'
        self.sell_ticker = 'S&P 500'
        self.buy_value = ''
        self.sell_value = ''
        self.period = '10 years'
        self.val_dict = {'Close price': 'Clp',
                         'MovAve(x)': 'MvAv(x)',
                         'Optimize_f[x1, x2]': 'Opt_f[x1, x2]'}

        buy_label = tk.Label(self.bt_window, text='Buy condition:')
        sell_label = tk.Label(self.bt_window, text='Sell condition:')
        self.buy_text = tk.Text(self.bt_window, width=40, height=10)
        self.sell_text = tk.Text(self.bt_window, width=40, height=10)
        expr_buy_button = ttk.Button(self.bt_window, text='Get buy expression',
                                     command=lambda: self.get_expr(self.buy_ticker,
                                                                   self.buy_value,
                                                                   expression='Buy'))
        expr_sell_button = ttk.Button(self.bt_window, text='Get sell expression',
                                      command=lambda: self.get_expr(self.sell_ticker,
                                                                    self.sell_value,
                                                                    expression='Sell'))
        execute_button = ttk.Button(self.bt_window, text='Backtest',
                                    command=lambda: self.execute(self.buy_text.get("1.0", tk.END),
                                                                 self.sell_text.get("1.0", tk.END)))
        store_button = ttk.Button(self.bt_window, text='Store algorithm',
                                  command=lambda: self.write_algorithm_to_textfile())
        load_button = ttk.Button(self.bt_window, text='Load algorithm', command=self.open_file_dialog)
        self.name_entry = ttk.Entry(self.bt_window, width=20)
        self.name_entry.insert(0, 'Name of algorithm')

        self.capita_entry = ttk.Entry(self.bt_window, width=15)
        #capita_entry.insert(0, 'Starting capita')
        self.commission_entry = ttk.Entry(self.bt_window, width=15)
        #commission_entry.insert(0, 'Commission')

        self.menu_button_period = ttk.Menubutton(self.bt_window, text='Period')
        self.menu_button_ticker_buy = ttk.Menubutton(self.bt_window, text='buy ticker')
        self.menu_button_value_buy = ttk.Menubutton(self.bt_window, text='value')
        self.menu_button_ticker_sell = ttk.Menubutton(self.bt_window, text='sell ticker')
        self.menu_button_value_sell = ttk.Menubutton(self.bt_window, text='value')
        menu_period = tk.Menu(self.menu_button_period)
        menu_ticker_buy = tk.Menu(self.menu_button_ticker_buy)
        menu_value_buy = tk.Menu(self.menu_button_value_buy)
        menu_ticker_sell = tk.Menu(self.menu_button_ticker_sell)
        menu_value_sell = tk.Menu(self.menu_button_value_sell)

        for asset in user_specific_object.get_shortlist():
            menu_ticker_buy.add_command(label=asset, command=lambda a=asset: self.set_buy_ticker(a))
            menu_ticker_sell.add_command(label=asset, command=lambda a=asset: self.set_sell_ticker(a))

        for value in self.val_dict:
            menu_value_buy.add_command(label=value, command=lambda v=value: self.set_buy_value(v))
            menu_value_sell.add_command(label=value, command=lambda v=value: self.set_sell_value(v))

        for period in financial_data.get_yfinance_periods():
            menu_period.add_command(label=period, command=lambda p=period: self.set_period(p))

        self.menu_button_ticker_buy["menu"] = menu_ticker_buy
        self.menu_button_ticker_sell["menu"] = menu_ticker_sell
        self.menu_button_value_buy["menu"] = menu_value_buy
        self.menu_button_value_sell["menu"] = menu_value_sell
        self.menu_button_period["menu"] = menu_period

        buy_label.place(relx=0.01, rely=0.01)
        self.buy_text.place(relx=0.01, rely=0.05)
        sell_label.place(relx=0.01, rely=0.46)
        self.sell_text.place(relx=0.01, rely=0.5)
        execute_button.place(relx=0.62, rely=0.4)
        self.capita_entry.place(relx=0.03, rely=0.4)
        self.commission_entry.place(relx=0.23, rely=0.4)
        self.menu_button_ticker_buy.place(relx=0.7, rely=0.05)
        self.menu_button_ticker_sell.place(relx=0.7, rely=0.5)
        self.menu_button_value_buy.place(relx=0.7, rely=0.1)
        self.menu_button_value_sell.place(relx=0.7, rely=0.55)
        self.menu_button_period.place(relx=0.45, rely=0.4)
        expr_buy_button.place(relx=0.7, rely=0.15)
        expr_sell_button.place(relx=0.7, rely=0.6)
        self.name_entry.place(relx=0.1, rely=0.85)
        store_button.place(relx=0.4, rely=0.85)
        load_button.place(relx=0.4, rely=0.9)

        # # FOR TESTING:
        self.buy_text.insert(tk.END, user_specific_object.algorithm['Buy Condition'])
        self.sell_text.insert(tk.END, user_specific_object.algorithm['Sell Condition'])
        self.capita_entry.insert(0, cap_def)
        self.commission_entry.insert(0, com_def)
        period = '10 years'
        self.menu_button_period.configure(text=per_def)

        #self.bt_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        #self.bt_window.withdraw()
        self.bt_window.mainloop()

    def show_window(self):
        print('test')
        self.bt_window.deiconify()

    def on_closing(self):
        self.bt_window.withdraw()

    def set_buy_ticker(self, asset):
        self.buy_ticker = asset
        self.menu_button_ticker_buy.configure(text=asset)

    def set_sell_ticker(self, asset):
        self.sell_ticker = asset
        self.menu_button_ticker_sell.configure(text=asset)

    def set_buy_value(self, value):
        self.buy_value = value
        self.menu_button_value_buy.configure(text=value)

    def set_sell_value(self, value):
        self.sell_value = value
        self.menu_button_value_sell.configure(text=value)

    def set_period(self, per):
        self.period = per
        self.menu_button_period.configure(text=per)

    def get_expr(self, asset, val, expression=''):
        ticker = user_specific_object.get_shortlist()[asset]
        val_syntax = self.val_dict[val]
        if expression == 'Sell':
            self.sell_text.insert(tk.END, str(ticker) + '.' + str(val_syntax))
        elif expression == 'Buy':
            self.buy_text.insert(tk.END, str(ticker) + '.' + str(val_syntax))
        else:
            popupmsg('An error occured. In get_expr.')

    def execute(self, buy_condition, sell_condition):
        buy_condition = self.buy_text.get("1.0", tk.END)
        sell_condition = self.sell_text.get("1.0", tk.END)

        # Needs some check to see if commission, capita, buy_condition and sell_condition
        # is valid.
        if not self.capita_entry.get().isnumeric() or not self.commission_entry.get().isnumeric():
            popupmsg('Capita and Commision needs to be numeric!')
            exit()

        ticker = user_specific_object.get_shortlist()[self.buy_ticker]
        per = financial_data.get_yfinance_period_value(self.period)
        df = financial_data.get_stock_history_based_on_period(ticker, per)['Close'].to_frame()
        dec_obj = Decision(df)

        if 'Opt_f[' in buy_condition and 'Opt_f[' in sell_condition:
            popupmsg('Cannot use optimization function in both buy and sell algorithm')
            exit()

        elif 'Opt_f[' in buy_condition or 'Opt_f' in sell_condition:
            paper_value_opt = []
            paper_value_max = -1
            ma_opt = -1
            df_opt = pd.DataFrame()
            if 'Opt_f[' in buy_condition:
                print('User wants to optimize buy algorithm')
                [x1, x2] = [int(x) for x in dec_obj.get_range_of_optimization_function(buy_condition)]
                df_opt['ma_opt'] = [x for x in range(x1, x2+1)]

                for x in range(x1, x2+1):
                    buy_cond_test = dec_obj.fill_in_ma(buy_condition, x)
                    df['Decision'] = dec_obj.make_decision(buy_cond_test, sell_condition)
                    print(x, x2)
                    df['PaperValue'] = self.calculate_paper_value(df)
                    paper_value_last_day = df.iloc[-1]['PaperValue']
                    paper_value_opt.append(paper_value_last_day)
                    if paper_value_last_day > paper_value_max:
                        paper_value_max = paper_value_last_day
                        ma_opt = x

                buy_condition = dec_obj.fill_in_ma(buy_condition, ma_opt)

            else:
                print('User wants to optimize sell algorithm')
                [x1, x2] = [int(x) for x in dec_obj.get_range_of_optimization_function(sell_condition)]
                df_opt['ma_opt'] = [x for x in range(x1, x2 + 1)]

                for x in range(x1, x2 + 1):
                    sell_cond_test = dec_obj.fill_in_ma(sell_condition, x)
                    df['Decision'] = dec_obj.make_decision(buy_condition, sell_cond_test)
                    print(x, x2)
                    df['PaperValue'] = self.calculate_paper_value(df)
                    paper_value_last_day = df.iloc[-1]['PaperValue']
                    paper_value_opt.append(paper_value_last_day)
                    if paper_value_last_day > paper_value_max:
                        paper_value_max = paper_value_last_day
                        ma_opt = x

                sell_condition = dec_obj.fill_in_ma(sell_condition, ma_opt)

            df_opt['PaperValue'] = paper_value_opt
            self.show_optimization(df_opt, ma_opt)

            # Show backtesting of optimal ma
            df['Decision'] = dec_obj.make_decision(buy_condition, sell_condition)
            df['PaperValue'] = self.calculate_paper_value(df)
            paper_value_last_day = df.iloc[-1]['PaperValue']
            self.show_backtesting(df, paper_value_last_day)

        else:

            try:
                df['Decision'] = dec_obj.make_decision(buy_condition, sell_condition)
            except SyntaxError:
                popupmsg('Buy condition and/or sell condition possibly wrong. Try again!')
                exit()

            self.buy_cond = buy_condition
            self.sell_cond = sell_condition
            user_specific_object.algorithm['Buy Condition'] = buy_condition
            user_specific_object.algorithm['Sell Condition'] = sell_condition

            df['PaperValue'] = self.calculate_paper_value(df)
            paper_value_last_day = df.iloc[-1]['PaperValue']

            self.show_backtesting(df, paper_value_last_day)

    def show_backtesting(self, df, paper_value_last_day):
        bt_fig_window = tk.Tk()
        paper_value_algorithm_label = tk.Label(bt_fig_window, text='Paper value of algorithm at end day: '
                                                                   + str(paper_value_last_day))
        canvas = FigureCanvasTkAgg(plotting_obj.plot_backtesting(df), bt_fig_window)
        canvas.draw()
        canvas.get_tk_widget().pack()
        paper_value_algorithm_label.pack()

    def show_optimization(self, df, ma_opt):
        opt_fig_window = tk.Tk()

        canvas = FigureCanvasTkAgg(plotting_obj.plot_optimization(df, ma_opt), opt_fig_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def calculate_paper_value(self, df):
        cap = float(self.capita_entry.get())
        com = float(self.commission_entry.get())
        tot = cap
        amount_asset = 0
        paper_value = []

        for index, row in df.iterrows():
            if row['Decision'] == 'Buy' and tot > row['Close']:
                tot -= com
                amount_asset = int(tot / row['Close'])
                tot -= (amount_asset * row['Close'])
            elif row['Decision'] == 'Sell' and amount_asset > 0:
                tot -= com
                tot += (amount_asset * row['Close'])
                amount_asset = 0
            paper_value.append(tot + amount_asset * row['Close'])

        return paper_value

    def write_algorithm_to_textfile(self):
        name = self.name_entry.get()
        buy_cond = self.buy_text.get("1.0", tk.END)
        sell_cond = self.sell_text.get("1.0", tk.END)

        folder = r'C:\Users\Emil\PycharmProjects\tkinter_tutorial\Algorithms'
        filepath = '\\'.join([folder, name]) + '.txt'
        df = pd.DataFrame()
        buy_cond_list = [buy_cond]
        df['Buy Condition'] = buy_cond_list
        sell_cond_list = [sell_cond]
        df['Sell Condition'] = sell_cond_list
        df.to_csv(filepath, index=False)

    def open_file_dialog(self):
        file = filedialog.askopenfilename(initialdir=r'C:\Users\Emil\PycharmProjects\tkinter_tutorial\Algorithms')
        if file:
             # Take data from .csv file for new shortlist
            algo_df = pd.read_csv(file)  # algorithm in type df
            print(algo_df)
            self.buy_cond = algo_df.iloc[0]['Buy Condition']
            self.sell_cond = algo_df.iloc[0]['Sell Condition']
            user_specific_object.set_algorithm(self.buy_cond, self.sell_cond)

            # First delete value of text widgets.
            self.buy_text.delete(1.0, tk.END)
            self.sell_text.delete(1.0, tk.END)

            # Then insert algorithm
            self.buy_text.insert(1.0, self.buy_cond)
            self.sell_text.insert(1.0, self.sell_cond)


plotting_obj = Plotting()
plotting_obj.set_user_obj(user_specific_object)

app = PersonalFinancialDashboardApp()
app.geometry(general_config_object.app_geometry)

app.mainloop()










