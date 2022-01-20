# Various small matplotlib-related utilities used across various DNA modules

import numpy as np
import PySimpleGUI as sg

from abc import ABC
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from utilities import encoded_logo

ix = 0.0
iy = 0.0


class Toolbar(NavigationToolbar2Tk, ABC):
    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)


def display_horiz_histogram(y_values: tuple, x_values: tuple, x_label: str, title: str):
    """
    Display a horizontal bar chart/histogram using matplotlib.

    :param y_values: The y-axis (horizontal) values
    :param x_values: The x-axis (vertical) values
    :param x_label: The labels on the x-axis (MUST correspond to the order of the values)
    :param title: The title of the histogram chart
    :returns: None (Histogram is displayed)
    """
    # Define the histogram
    plt.rcdefaults()
    fig, ax = plt.subplots()
    y_pos = np.arange(len(y_values))
    ax.barh(y_pos, x_values, align='edge')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_values)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlabel(x_label)
    plt.tight_layout(pad=2.0)
    # Display in a window
    layout = [[sg.Canvas(key="-CANVAS-")]]
    window_histogram = sg.Window(title, layout, icon=encoded_logo, element_justification='center',
                                 finalize=True)
    draw_figure(window_histogram["-CANVAS-"].TKCanvas, fig)
    # Non-blocking window
    window_histogram.read(timeout=0)
    return


def draw_figure(canvas, figure) -> FigureCanvasTkAgg:
    """
    Routine to draw a matplotlib image on a tkinter canvas (adapted from a demo program at
    https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Matplotlib.py).

    :param canvas: The 'canvas' object in PySimpleGUI
    :param figure: The matplotlib figure to be drawn
    :returns: The tkinter canvas which will contain the figure
    """
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg


def draw_figure_with_toolbar(canvas, fig, canvas_toolbar) -> FigureCanvasTkAgg:
    """
    Routine to draw a matplotlib image, with a toolbar, on a tkinter canvas (adapted from a demo program at
    https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Matplotlib_Embedded_Toolbar.py).

    :param canvas: The 'canvas' object in PySimpleGUI
    :param fig: The matplotlib figure to be drawn
    :param canvas_toolbar: The 'toolbar' part of the 'canvas' object in PySimpleGUI
    :returns: The tkinter canvas which will contain the figure
    """
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)
    toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg
