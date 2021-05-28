import PySimpleGUI as sg

from encoded_images import encoded_logo

# Help text, Each line should be 70 chars or less
scrolled_existing = \
    "Choose the 'Load Narratives From Existing Store' option when narratives have \n" \
    "already been ingested to a backing store. A list of the currently available stores \n" \
    "is displayed in a new window, and one can be selected for study and analysis. (In \n" \
    "addition, a store can be deleted, if no longer needed.) The selected store will be \n" \
    "noted (directly below the 'Load Narratives' section in the main window) along with \n" \
    "a count of the contained narratives."

scrolled_csv = \
    "Choose the 'Load Narratives From CSV Metadata' option when ingesting new narratives \n" \
    "into a new or existing store. A file browser window is displayed to select the CSV file. \n" \
    "In addition, a list of the currently available stores is displayed to allow the \n" \
    "narratives to be added to one of them, or a new store can be defined.\n\n" \
    "The CSV format is SPECIFIC TO THE DOMAIN being investigated.\n\n" \
    "Note that the processing may take SEVERAL MINUTES if many narratives are ingested. \n\n" \
    "For the Holocaust narratives, most are parsed from .PDF files. Therefore, the \n" \
    "details of the start/end pages (within the PDF), header/footer keywords, ... are \n" \
    "and used for automated extraction and cleanup of the text. Minimal information \n" \
    "on the narrator/subject of the text is also specified (such as the person's name \n" \
    "and gender. Other information (such as date and location of the person's birth) \n" \
    "are extracted from the text itself. \n\n" \
    "For the Holocaust narratives, the format of the CSV Metadata file is: \n" \
    "   Source,Title,Person,Given,Given2,Surname,Maiden,Maiden2,Gender, \n" \
    "   Start,End,Remove,Header,Footer \n" \
    "where: \n" \
    "   * Source is the filename of the narrative \n" \
    "     The file MUST be stored in the dna/resources directory\n" \
    "     (Note that this can be a .txt or .pdf file) \n" \
    "   * Title is a free-form string which will be used to identify the narrative \n" \
    "   * Person is either 1 or 3 indicating whether the narrative is written in the first or \n" \
    "     third person \n" \
    "   * Given, Surname and Maiden are free-form strings defining the first, last and \n" \
    "     maiden names of the narrator/person whose narrative is defined \n" \
    "     (Note that a unique Given name/identifier MUST be specified for each narrator/\n" \
    "     subject to distinguish between them. This identifier can obfuscate the name \n" \
    "     of the narrator/subject.) \n" \
    "   * Given2 and Maiden2 are additional strings denoting that the narrator/subject \n" \
    "     changed their given name (perhaps when they emigrated to another country), \n" \
    "     and/or were married more than once. \n" \
    "   * Gender is either M, F, A, B, U indicating male, female, agender, bigender or \n" \
    "     unknown, respectively \n" \
    "   * Start and End are only used when the Source file is PDF and indicates the specific \n" \
    "     page(s) that should be extracted and processed to become the stored narrative \n" \
    "     (Note that only single column PDFs can be processed at this time) \n" \
    "   * Remove defines the number of lines to be removed from the text file created from \n" \
    "     the PDF. For the Holocaust narratives, there are anywhere from 1 to 6 lines \n" \
    "     removed (title, subject, sometimes a brief overview of the person's life, etc.) \n" \
    "   * Header and Footer are only used when the Source file is PDF and are sets of words \n" \
    "     separated by semi-colons, ;) such that if a line of text contains all the words, \n" \
    "     then that line will be discarded (Note that the words are case sensitive) \n\n" \
    "After the narratives are ingested, the selected store will be noted (directly below \n" \
    "the 'Load Narratives' section in the main window) along with a count of the contained \n" \
    "narratives."

scrolled_stats = \
    "After selecting the narrative store, choose 'Summary Statistics' to open a new window \n" \
    "where various graphs and charts can be selected for display, or a list of the most \n" \
    "frequent words can be displayed. The charts describe various characteristics of the \n" \
    "narrators and other information, such as the locations and times mentioned in the \n" \
    "stories. The graphs display word clouds, clusters of semantically similar narratives, 'n" \
    "etc. In addition, a list of frequent terms can be downloaded to a CSV file and used \n" \
    "to extend the ontology, to create a gazetteer, or for other uses.\n\n" \
    "The statistics can be TAILORED TO THE DOMAIN being investigated. \n\n" \
    "The number and variety of default graphs and charts will expand based on user feedback."

scrolled_search = \
    "After selecting the store, choose 'Narrative Search/Display' to open a new window to \n" \
    "review and search the texts and metadata of all the ingested narratives, and to select \n" \
    "one or more for display. For each of the selected narratives, its metadata and text are \n" \
    "available as well as a timeline of its events and conditions."

scrolled_similarities = \
    "After selecting the narrative store, choose 'Narrative Similarities' to open a new window  \n" \
    "displaying sequences of events and conditions which occur in two or more narratives. A \n" \
    "list of the sequences is shown with the number of narratives where that sequence occurs."

scrolled_hypothesis = \
    "Make sure that a narrative store is selected above and then choose 'Hypothesis \n" \
    "Search/Edit' to open a new window to review and edit existing hypotheses, or to define \n" \
    "new ones. Hypotheses are lists or series of events and conditions which are investigated \n" \
    "by 'Hypothesis Test'. The latter searches for evidence of the occurrence of these events, \n" \
    "conditions or sequences in the narratives."

scrolled_test = \
    "Choose 'Hypothesis Test' to select an hypothesis and then search for supporting evidence in \n" \
    "the narratives defined above (in 'Load Narratives'). A list of the currently available \n" \
    "hypotheses is displayed in a new window, and one can be selected for study and analysis. \n" \
    "Hypotheses are lists or series of events and conditions which are searched for, in the \n" \
    "narratives. Note that this search allows both querying for the occurrence of events \n" \
    "and conditions in any order, or for their occurrence in a specific sequence. The \n" \
    "latter does NOT require, however, that the occurrences are strictly sequential, but \n" \
    "can be separated by other intervening events and conditions. Results of the search \n" \
    "detail the specific narratives where the occurrences are found and the ones where \n" \
    "they are NOT found. Summary statistics are displayed for the positive and negative \n" \
    "narratives."

# Dictionaries tying help text and popup window title to the event
text_dict = {'existing_question': scrolled_existing,
             'csv_question': scrolled_csv,
             'similarities_question': scrolled_similarities,
             'search_question': scrolled_search,
             'stats_question': scrolled_stats,
             'hypothesis_question': scrolled_hypothesis,
             'test_question': scrolled_test}

title_dict = {'existing_question': "Help for 'From Existing Source'",
              'csv_question': "Help for 'From CSV Metadata'",
              'similarities_question': "Help for 'Narrative Similarities'",
              'search_question': "Help for 'Narrative Search/Display'",
              'stats_question': "Help for 'Summary Statistics'",
              'hypothesis_question': "Help for 'Create/Review/Edit Hypothesis'",
              'test_question': "Help for 'Test Hypothesis'"}


def display_popup_help(event: str):
    """
    Displays 'scrolled' help text in a popup window.

    :param event: String indicating the specific help text that should be displayed.
                  This value is taken from the layout's 'key' indicating which button was pressed,
                  and is then mapped to the window's title (using this module's title_dict) and
                  to the specific text (using this module's text_dict).
    :return: No info returned. This method returns upon closing the popup.
    """
    sg.popup_scrolled(text_dict[event], font=('Arial', 14),
                      size=(72, 15), text_color='black',
                      title=title_dict[event], background_color='white',
                      button_color='dark blue', icon=encoded_logo)
