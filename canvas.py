# External modules:
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import MultiCursor

# Internal modules:
from plotting import Plotting


class Canvas:

    def __init__(self):
        self._multicursor = None
        self._figure_canvas_agg = None
        self._plotting_object = Plotting()
        self._user_input = None
        self._fig = None
        self._axlist = None

    def set_user_input(self, user_inp):
        self._user_input = user_inp

    def set_figure_canvas_agg(self, figure_canvas_agg):
        self._figure_canvas_agg = figure_canvas_agg

    def draw_canvas(self, canvas_fig, canvas_toolbox):
        self._plotting_object.set_user_input(self._user_input)
        self._fig, self._axlist = self._plotting_object.plot()

        self._clear_canvas(canvas_fig, canvas_toolbox)
        self._embed_figure_to_tkinter_canvas(canvas_fig)
        self._embed_cursor_to_tkinter_canvas()
        self._embed_toolbar_to_tkinter_canvas(canvas_toolbox)
        self._pack_canvas_to_tkinter()

    def _clear_canvas(self, canvas_fig, canvas_toolbox):
        if canvas_fig.TKCanvas.children:
            for child in canvas_fig.TKCanvas.winfo_children():
                child.destroy()
        if canvas_toolbox.TKCanvas.children:
            for child in canvas_toolbox.TKCanvas.winfo_children():
                child.destroy()

    def _embed_figure_to_tkinter_canvas(self, canvas_fig):
        self._figure_canvas_agg = FigureCanvasTkAgg(self._fig, master=canvas_fig.TKCanvas)
        self._figure_canvas_agg.draw()

    def _embed_toolbar_to_tkinter_canvas(self, canvas_toolbox):
        toolbar = NavigationToolbar2Tk(self._figure_canvas_agg, canvas_toolbox.TKCanvas)
        toolbar.update()

    def _embed_cursor_to_tkinter_canvas(self):
        # Create a cursor for axlist. Needs to be attribute to be responsive.
        # useblit makes the performance much better.
        self._multicursor = MultiCursor(self._figure_canvas_agg, self._axlist, lw=1, useblit=True)

        # function read_cursor_value is called while hovering over the canvas
        self._figure_canvas_agg.mpl_connect('motion_notify_event', self._plotting_object.create_cursor_value)

    def _pack_canvas_to_tkinter(self):
        self._figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=True)


