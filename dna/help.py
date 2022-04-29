# Displays various help texts in a popup window
# Called by app.py

import PySimpleGUI as sg

from utilities import encoded_logo

# Help text, Each line should be 70 chars or fewer
scrolled_existing = \
    "Choose the 'Load Narratives From Existing Store' option when narratives have \n" \
    "already been ingested to the backing store. A list of the currently available \n" \
    "databases is displayed in a new window, and one can be selected for study and \n" \
    "analysis. (In addition, in the future, a database can be deleted, if no longer \n" \
    "needed.) The selected database will be noted (directly below the 'Load \n" \
    "Narratives' section in the main window) along with a count of the contained \n" \
    "narratives."

scrolled_csv = \
    "Choose the 'Load Narratives From CSV Metadata' option when ingesting new narratives \n" \
    "into a new or existing database. A file browser window is displayed to select the \n" \
    "CSV file. In addition, a list of the currently available databases is displayed to \n" \
    "allow the narratives to be added to one of them, or a new store can be defined.\n\n" \
    "The CSV fields are SPECIFIC TO THE DOMAIN being investigated, although several  \n" \
    "items (such as narrator identification or header/footer identification in PDFs) will \n" \
    "be generalized and generically available for reuse. This, however, is not a goal of \n" \
    "the current work. Note that in the simplest case, the file need only identify a list \n" \
    "of text files to be ingested.\n\n" \
    "Note that the processing may take SEVERAL MINUTES if many narratives are ingested. \n\n" \
    "For the Holocaust narratives, most are parsed from .PDF files. Therefore, the \n" \
    "details of the start/end pages (within the PDF), header/footer keywords, etc. are \n" \
    "used to automate the extraction and cleanup of the text. Minimal information \n" \
    "on the narrator/subject of the text is also specified (such as the person's name \n" \
    "and gender). However, metadata is not restricted to what is in the CSV file. To \n" \
    "illustrate what can be extracted from the text alone, other information (e.g., \n" \
    "the date and location of the narrator's birth) are extracted from the texts and \n" \
    "added to the database.\n\n" \
    "For the Holocaust narratives, the format of the CSV Metadata file is: \n" \
    "   Source,Title,Person,Type, Given,Given2,Surname,Maiden,Maiden2, \n" \
    "   Gender,Start,End,Remove,Header,Footer \n" \
    "where: \n" \
    "   * Source is the filename of the narrative \n" \
    "     The file MUST be stored in the dna/resources directory\n" \
    "     (Note that this can be a .txt or .pdf file) \n" \
    "   * Title is a free-form string which will be used to identify the narrative \n" \
    "   * Person is either 1 or 3 indicating whether the narrative is written in the first or \n" \
    "     third person \n" \
    "   * Type is either 'T' or 'E' indicating whether the story is a timeline/life history \n" \
    "     of the narrator or the narrative related to an episode in the narrator's life \n" \
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
    "After the narratives are ingested, the selected database will be noted (directly below \n" \
    "the 'Load Narratives' section in the main window) along with a count of the contained \n" \
    "narratives."

scrolled_edit = \
    "After selecting the narrative database, click on 'Edit Narrative' to open a new \n" \
    "window and choose one of the ingested narratives for editing. The narrative's \n" \
    "nouns/concepts or events can be selected for edit. A table of the nouns and their " \
    "details, and/or the sentence text and event details will be shown. \n\n" \
    "Note that new concepts/nouns and events can be added, while existing ones can be updated \n" \
    "or removed."

scrolled_stats = \
    "After selecting the narrative database, choose 'Summary Statistics' to open a new \n" \
    "window and display a variety of graphs and charts. The goal is to allow a researcher \n" \
    "to understand the demographics of their narrators, and determine if they reflect the\n" \
    "backing population.\n\n" \
    "The output displays are TAILORED TO THE DOMAIN being investigated. The number and \n" \
    "variety of graphs and charts will expand based on user feedback.\n\n" \
    "In this demo, the graphs display word clouds, clusters of semantically similar \n" \
    "narratives, and more. The charts illustrate different characteristics of the \n" \
    "narrators (such as their genders or birth years), as well as other information \n" \
    "(such as the locations and times mentioned in the texts).\n\n" \
    "When INDICATED BY THE DOMAIN, it may be possible to identify if the same narrator \n" \
    "has provided multiple narratives - and 'unify' the different narrator references. This \n" \
    "processing is illustrated in this demo (based on the narrator's given name and surname), \n" \
    "since there are numerous Holocaust-related narratives associated with and provided by \n" \
    "a single individual.\n\n" \
    "Lastly, a list of frequent terms whose semantics are not captured in the backing " \
    "DNA ontology (i.e., are 'unknown') can be output and used to extend the ontology.\n" \
    "Future releases of the DNA tooling will aid in performing this extension.\n\n" \
    "Note that the output displays are TAILORED TO THE DOMAIN being investigated. And, \n" \
    "the number and variety of default graphs and charts will expand based on user \n" \
    "feedback."

scrolled_timeline = \
    "After selecting the database, click on 'Narrative Timeline' to open a new window \n" \
    "to choose either a timeline of domain-specific events (if applicable) or one of \n" \
    "the ingested narratives for display. For a narrative, the metadata, story text and \n" \
    "a timeline plot are displayed. For the domain details, only a timeline is displayed.\n\n" \
    "From the timeline, a date (YYYY-mm) can be entered to obtain a network diagram of \n" \
    "the events that occurred in that month and year.\n\n" \
    "In a future release, it will be possible to compare timelines (for example, a news \n" \
    "event timeline, an aid or medical treatment timeline, and the narrative timeline) both \n" \
    "visually (in a single figure) and programmatically. At present, the windows with the \n" \
    "individual timelines can be kept open and compared."

scrolled_similarities = \
    "After selecting the narrative database, choose 'Narrative Similarities' to open a new \n" \
    "window displaying sequences of events and conditions which occur in two or \n" \
    "more narratives. A list of the sequences is shown with the number of narratives \n" \
    "where that sequence occurs."

scrolled_hypothesis = \
    "Make sure that a narrative database is selected above and then choose 'Hypothesis \n" \
    "Search/Edit' to open a new window to review and edit existing hypotheses, or to define \n" \
    "new ones. Hypotheses are patterns - lists or series of events, conditions and requirements " \
    "(such as the gender or education level of the narrator) which are searched for (using \n" \
    "'Hypothesis Test'), in the narratives and metadata."

scrolled_test = \
    "Choose 'Hypothesis Test' to select an hypothesis and then search for supporting/refuting \n" \
    "evidence in the narratives defined above (in 'Load Narratives'). A list of the currently \n" \
    "available hypotheses is displayed in a new window, and one can be selected for study and \n" \
    "analysis. Hypotheses are patterns - lists or series of events, conditions and requirements " \
    "(such as the gender or education level of the narrator) which are searched for, in the " \
    "narratives and metadata.\n\n" \
    "Search allows both querying for the occurrence of events and conditions in any order, \n" \
    "or for their occurrence in a specific sequence. The latter does NOT require, however, \n" \
    "that the occurrences are strictly sequential, but can be separated by other intervening  \n" \
    "events and conditions. Results of the search detail the specific narratives where the \n" \
    "occurrences are found and the ones where they are NOT found. Summary statistics are \n" \
    "displayed for the positive and negative narratives to aid in expanding or restricting \n" \
    "the hypotheses."

# Dictionaries tying help text and popup window title to the event
text_dict = {'existing_question': scrolled_existing,
             'csv_question': scrolled_csv,
             'edit_question': scrolled_edit,
             'similarities_question': scrolled_similarities,
             'timeline_question': scrolled_timeline,
             'stats_question': scrolled_stats,
             'hypothesis_question': scrolled_hypothesis,
             'test_question': scrolled_test}

title_dict = {'existing_question': "Help for 'From Existing Source'",
              'csv_question': "Help for 'From CSV Metadata'",
              'edit_question': "Help for 'Edit Narrative'",
              'similarities_question': "Help for 'Narrative Similarities'",
              'timeline_question': "Help for 'Narrative Timeline'",
              'stats_question': "Help for 'Summary Statistics'",
              'hypothesis_question': "Help for 'Create/Review/Edit Hypothesis'",
              'test_question': "Help for 'Test Hypothesis'"}


def display_popup_help(event: str):
    """
    Displays 'scrolled' help text in a popup window.

    :param event: String indicating the specific help text that should be displayed where
                  the value is taken from the layout's 'key' indicating which button was pressed,
                  and is then mapped to the window's title (using this module's title_dict) and
                  to the specific text (using this module's text_dict)
    :returns: No info returned. This method returns upon closing the popup
    """
    sg.popup_scrolled(text_dict[event], font=('Arial', 14),
                      size=(72, 15), text_color='black',
                      title=title_dict[event], background_color='white',
                      button_color='dark blue', icon=encoded_logo)
