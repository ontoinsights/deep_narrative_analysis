# Processing to display various graphs/charts concerning the characteristics of the narrators
# and their stories, or related to nouns/verbs which are not 'known'/understood by the ontology

from abc import ABC
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.ticker import MaxNLocator
import numpy as np
from wordcloud import WordCloud, STOPWORDS

from database import query_database
from utilities import empty_string

ix = 0.0
iy = 0.0

narrator_var = "?narrator"

query_narrative_text = 'prefix : <urn:ontoinsights:dna:> SELECT ?text WHERE ' \
                       '{ ?narr a :Narrative ; rdfs:label "narrative_name" ; :text ?text . }'

query_metadata1 = 'prefix : <urn:ontoinsights:dna:> SELECT ?name WHERE ' \
                  '{ ?narrator rdfs:label ?name }'

query_metadata2 = 'prefix : <urn:ontoinsights:dna:> SELECT ?year ?country WHERE ' \
                  '{ ?birthEvent a :Birth ; :has_affected_agent ?narrator . ' \
                  'OPTIONAL { ?birthEvent :has_time/:year ?year } ' \
                  'OPTIONAL { ?birthEvent :has_location/:country_name ?country } }'

query_metadata3 = 'prefix : <urn:ontoinsights:dna:> SELECT ?aspect WHERE ' \
                  '{ ?narrator :has_agent_aspect ?aspect }'

query_years = 'prefix : <urn:ontoinsights:dna:> SELECT distinct ?s ?year WHERE ' \
              '{ ?narr a :Narrative ; :has_author ?narrator . ?event a :Birth ; ' \
              ':has_affected_agent ?narrator ; :has_time/:year ?year . { ?narrator a :Person . ' \
              'FILTER NOT EXISTS { ?unifying1 a :UnifyingCollection ; :has_member ?narrator } . ' \
              'BIND (?narrator as ?s) } UNION { ?unifying2 a :UnifyingCollection ; :has_member ?narrator . ' \
              'BIND (?unifying2 as ?s) } }'


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


def display_timeline(narrative_name: str, store_name: str):
    """
    Displays a timeline of the narrative or domain events using a matplotlib stem plot.

    :param narrative_name: The name/label of the narrative
    :param store_name: The database/store to be queried for data
    :returns: None (timeline is displayed)
    """
    logging.info(f'Displaying narrative timeline for {narrative_name}')
    event_dict = dict()
    for binding in event_list:
        if 'month' in binding.keys():
            dict_key = f'{binding["year"]["value"]}-{binding["month"]["value"]}'
        else:
            dict_key = f'{binding["year"]["value"]}-01'
        add_to_dictionary_values(event_dict, dict_key, binding['label']['value'], str)

    dates = []
    texts = []
    for key, value in event_dict.items():
        dates.append(key)
        texts.append('\n'.join(value))
    # For matplotlib timeline, need datetime formatting
    plot_dates = [datetime.strptime(d, "%Y-%m") for d in dates]
    # Create a stem plot with some variation in levels as to distinguish close-by events.
    # Add markers on the baseline with dates
    # For each event, add a text label via annotate, which is offset from the tip of the event line
    levels = np.tile([-10, 10, -6, 6, -2, 2, -8, 8, -4, 4, -1, 1, -9, 9, -5, 5],
                     int(np.ceil(len(plot_dates) / 6)))[:len(plot_dates)]
    # Create figure and plot a stem plot with the dates
    fig, ax = plt.subplots(figsize=(20, 16))
    dpi = fig.get_dpi()
    fig.set_size_inches(808 * 2 / float(dpi), 808 / float(dpi))
    ax.set(title=narrative_name)
    ax.vlines(plot_dates, 0, levels, color="tab:red")  # The vertical stems
    ax.plot(plot_dates, np.zeros_like(plot_dates), "-o",
            color="k", markerfacecolor="w")  # Baseline and markers on it
    # Annotate lines
    for d, l, r in zip(plot_dates, levels, texts):
        ax.annotate(r, xy=(d, l),
                    xytext=(-2, np.sign(l) * 3), textcoords="offset points",
                    horizontalalignment="right",
                    verticalalignment="bottom" if l > 0 else "top", fontsize='x-small')
    # Format x-axis with yearly intervals
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize='small')
    # Remove y-axis and spines
    ax.yaxis.set_visible(False)
    ax.spines[["left", "top", "right"]].set_visible(False)
    ax.margins(y=0.1)
    plt.tight_layout(pad=0.05, h_pad=0.05, w_pad=0.05)
    plt.show()

    # Display in a window with matplotlib interactive controls
    # TODO: Add checkboxes to limit relationships that are displayed?
    layout = [[sg.Text('Display Event Network for Date (YYYY-mm): ', font=('Arial', 14)),
               sg.InputText(text_color='black', background_color='#ede8e8', size=(10, 1),
                            font=('Arial', 14), key='event_date', do_not_clear=True),
               sg.Button('Graph', button_color=dark_blue, font=('Arial', 14), size=(6, 1))],
              [sg.Text('Controls:', font=('Arial', 14)),
               sg.Canvas(key='controls_cv')],
              [sg.Column(layout=[[sg.Canvas(key='fig_cv', size=(800 * 2, 800))]], pad=(0, 0))]]
    window_timeline = sg.Window('Timeline', layout, icon=encoded_logo, element_justification='center',
                                resizable=True).Finalize()
    window_timeline['event_date'].Widget.config(insertbackground='black')
    draw_figure_with_toolbar(window_timeline['fig_cv'].TKCanvas, fig,
                             window_timeline['controls_cv'].TKCanvas)
    window_timeline.Maximize()
    while True:
        event, values = window_timeline.read()
        if event == 'Graph':
            display_graph(narrative_name, event_list, store_name, values['event_date'])
        if event == sg.WIN_CLOSED:
            break
    window_timeline.close()


def display_visualization(narr_detail: str, database: str):
    """
    Display a Word Cloud based on the texts of the narratives.

    :param narratives: String consisting of all the narratives' texts
    :param words_in_cloud: Integer value indicating the number of words to be displayed
    :returns: None (Word cloud is displayed)
    """


def display_word_cloud(narr_detail: str, database: str):
    """
    Display a Word Cloud based on the texts of the narratives.

    :param narratives: String consisting of all the narratives' texts
    :param words_in_cloud: Integer value indicating the number of words to be displayed
    :returns: None (Word cloud is displayed)
    """
    # Size the WordCloud plot
    plt.rcdefaults()
    fig, ax = plt.subplots()
    # Set stop-words (words to ignore)
    stopwords = set(STOPWORDS)
    stopwords.update(['will', 'per', 'us', 'said', 'even',
                      'one', 'two', 'first', 'second'])
    # Create WordCloud of top xx words in all documents
    wordcloud = WordCloud(stopwords=stopwords, max_font_size=50, max_words=words_in_cloud,
                          background_color='white').generate(narratives)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    # Display in a window
    layout = [[sg.Canvas(key="-CANVAS-")]]
    window_cloud = sg.Window("Word Cloud Based on Narratives' Texts", layout,
                             icon=encoded_logo, element_justification='center').Finalize()
    draw_figure(window_cloud["-CANVAS-"].TKCanvas, fig)
    window_cloud.read()


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
