# External modules:
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import MultiCursor

# Internal modules:
from plotting import Plotting


class Canvas:
    # Class for clearing and updating canvas for what the user requested (request comes from the UserInput object)

    def __init__(self):
        self._multicursor = None
        self._figure_canvas_tkagg = None
        self._plotting_object = Plotting()
        self._user_input = None
        self._fig = None
        self._axlist = None

    def set_user_input(self, user_input):
        self._user_input = user_input

    def draw_canvas(self, canvas_fig, canvas_toolbox):
        self._clear_canvases([canvas_fig, canvas_toolbox])

        self._plotting_object.set_user_input(self._user_input)
        self._fig, self._axlist = self._plotting_object.plot()

        # TkAgg is the backend where Agg (Anti-grain geometry) is the canonical renderer.
        # The renderer is what does the drawing. So TkAgg is the Agg rendering to a Tk canvas.
        # Check out matplotlib documentation for more information.
        self._figure_canvas_tkagg = self._get_embedded_figure_to_canvas_w_tkagg(canvas_fig)
        self._figure_canvas_tkagg.draw()

        self._create_cursor_to_tk_canvas()
        self._embed_mouse_hovering_as_cursor_to_tk_canvas()

        self._embed_toolbar_to_tk_canvas(canvas_toolbox)

        self._pack_canvas_to_tk()

    def _clear_canvases(self, list_of_canvases):
        # Clear canvases from earlier drawing of canvas.
        for canvas in list_of_canvases:
            if canvas.TKCanvas.children:
                for child in canvas.TKCanvas.winfo_children():
                    child.destroy()

    def _get_embedded_figure_to_canvas_w_tkagg(self, canvas_fig):  # tk = tkinter, agg = anti-grain geometry
        # TkAgg is the backend where Agg (Anti-grain geometry) is the canonical renderer.
        # The renderer is what does the drawing. So TkAgg is the Agg rendering to a Tk canvas.
        # Check out matplotlib documentation for more information.
        return FigureCanvasTkAgg(self._fig, master=canvas_fig.TKCanvas)

    def _embed_toolbar_to_tk_canvas(self, canvas_toolbox):
        # Uses TkAgg as backend since NavigationToolbar2Tk is imported from backend_tkagg.
        # TkAgg is the backend where Agg (Anti-grain geometry) is the canonical renderer.
        # The renderer is what does the drawing. So TkAgg is the Agg rendering to a Tk canvas.
        # Check out matplotlib documentation for more information.
        toolbar = NavigationToolbar2Tk(self._figure_canvas_tkagg, canvas_toolbox.TKCanvas)
        toolbar.update()

    def _create_cursor_to_tk_canvas(self):
        # Multicursor works for all backends as it is imported from matplotlib.widgets.
        # useblit: uses blitting for faster drawing. Supported by the backend TkAgg which is used.
        self._multicursor = MultiCursor(self._figure_canvas_tkagg, self._axlist, lw=1, useblit=True)

    def _embed_mouse_hovering_as_cursor_to_tk_canvas(self):
        # function create_cursor_value is called while hovering over the canvas with the mouse
        self._figure_canvas_tkagg.mpl_connect('motion_notify_event', self._plotting_object.create_cursor_value)

    def _pack_canvas_to_tk(self):
        # get_tk_widget() returns the tkinter widget used to implement FigureCanvasTkAgg
        # .pack() organizes widgets in blocks before placing them in the parent widget (returned by get_tk_widget()).
        # expand: if True, widget expands to fill any space not otherwise used in parent widget.
        # fill: Determines whether widget fills any extra space allocated to it by the packer,
        #       or keeps its own minimal dimensions. Possibilities: none, x(fill only horizontally),
        #       y(fill only vertically) and both.
        # side: Determines which side of the parent widget packs against. Possibilities: top, bottom, left and right.
        self._figure_canvas_tkagg.get_tk_widget().pack(side='right', fill='both', expand=True)


