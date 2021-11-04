# Text cleanup when loading narratives from pdfs or plain text
# Called by load.py

from utilities import empty_string, new_line, double_new_line


def clean_text(narrative: str, narr_metadata: dict) -> str:
    """
    Clean narrative text by:
      * Removing extraneous beginning white-space
      * Combining lines into paragraphs
      * Having 2 CR/LFs between paragraphs
      * Removing headers/footers (if they exist)
    This is typically only needed for pdf inputs, AND IS CUSTOMIZED for the specific pdf style.

    :param narrative: String holding the text to be processed
    :param narr_metadata: Dictionary of metadata information - Keys are: Source,Title,Person,Type,
                          Given,Given2,Surname,Maiden,Maiden2,Gender,Start,End,Remove,Header,Footer
    :return: Updated narrative text
    """
    new_text = empty_string
    # Split the text by the new lines/CRs since these are added by the PDF->text conversion
    if 'Remove' in narr_metadata.keys():
        # Remove the first x line(s) from the text, if a value is provided in the CSV
        lines = narrative.split(new_line)[int(narr_metadata['Remove']):]
    else:
        lines = narrative.split(new_line)
    ending_period_quote = False
    for line in lines:
        if not line:
            if ending_period_quote:
                new_text += double_new_line         # 2 CR/LFs between paragraphs
                ending_period_quote = False
            # Else, just ignore the line assuming that it is a blank line between text and footer/header
        else:
            # Remove header/footer lines (if any are defined)
            if 'Header' in narr_metadata.keys() and \
                    _check_header_footer_match(line, narr_metadata['Header'].split(';')):
                continue               # Skip line
            if 'Footer' in narr_metadata.keys() and \
                    _check_header_footer_match(line, narr_metadata['Footer'].split(';')):
                continue               # Skip line
            # Remove white space at beginning/ending of lines, and have 1 white space between words
            new_text += line.strip()
            # Remove dash at the end of a line (assumes that it is a hyphenated word) and don't add space
            # TODO: Is it ok to always assume that a dash at the end of a line is a hyphenated word?
            if new_text.endswith('-'):
                new_text = new_text[:-1]
            else:
                end_char = new_text[-1]
                if end_char in ['.', "'", '"']:
                    ending_period_quote = True
                new_text += ' '
    # Clean up final lines of text due to <NP> and other artifacts
    new_text = new_text.replace(' \n\n \n\n', ' \n').replace(' \n\n ', ' \n')
    return new_text


def simplify_text(narrative: str, narr_metadata: dict) -> str:
    """
    Update the text to change 3rd person instances of full name, given name + maiden name and
    given name + surname to 'Narrator', and to change instances of 'the {maiden_name}s' and 'the
    {surname}s' to 'family'. This is done to try to minimize co-reference problems.

    :param narrative: String holding the text to be processed
    :param narr_metadata: Dictionary of metadata information - Keys are: Source,Title,Person,Type,
                          Given,Given2,Surname,Maiden,Maiden2,Gender,Start,End,Remove,Header,Footer
    :return: Updated narrative text
    """
    new_text = narrative
    # If third person, simplify name to be 'Narrator'
    if narr_metadata['Person'] == '3':
        new_text = _replace_third_person(new_text, narr_metadata['Given'], narr_metadata)
        if narr_metadata['Given2']:
            new_text = _replace_third_person(new_text, narr_metadata['Given2'], narr_metadata)
    # Update occurrences of maiden name or surname to be 'family'
    if narr_metadata['Maiden']:
        maiden_name = narr_metadata['Maiden']
        new_text = new_text.replace(f"the {maiden_name}s", 'family').replace(f"The {maiden_name}s", 'Family')
    if narr_metadata['Maiden2']:
        maiden_name = narr_metadata['Maiden2']
        new_text = new_text.replace(f"the {maiden_name}s", 'family').replace(f"The {maiden_name}s", 'Family')
    if narr_metadata['Surname']:
        surname = narr_metadata['Surname']
        new_text = new_text.replace(f"the {surname}s", 'family').replace(f"The {surname}s", 'Family')
    return new_text


# Functions private to the module
def _check_header_footer_match(line: str, terms: list) -> bool:
    """
    Check the line of text if it includes all occurrences of the specified terms.

    :param line: String holding the line of text
    :param terms: Terms whose presence in the line are validated
    :return: True if all the specified terms are in the line (or if there are no terms defined)
             False otherwise
    """
    if len(terms) == 0:
        return False
    term_count = 0
    for term in terms:
        if term in line:
            term_count += 1
    if term_count == len(terms):
        return True
    else:
        return False


def _replace_third_person(narrative: str, given_name: str, narr_metadata: dict) -> str:
    """
    Update the text to change 3rd person instances of full name, given name + maiden name and
    given name + surname to "Narrator", and the possessive form to "Narrator's".

    :param narrative: String holding the narrative text
    :param given_name: The narrator's given name
    :param narr_metadata: Dictionary of metadata information - Keys are: Source,Title,Person,Type,
                          Given,Given2,Surname,Maiden,Maiden2,Gender,Start,End,Remove,Header,Footer
    :return: String with the updated text
    """
    new_text = narrative
    maiden_name = narr_metadata['Maiden']
    maiden2_name = narr_metadata['Maiden2']
    surname = narr_metadata['Surname']
    new_text = new_text.replace(f"{given_name}'s ", "Narrator's ")
    if maiden_name and surname:
        new_text = new_text.replace(f"{given_name} ({maiden_name}) {surname}'s ", "Narrator's ").\
            replace(f"{given_name} {maiden_name} {surname}'s ", "Narrator's ")
        new_text = new_text.replace(f"{given_name} ({maiden_name}) {surname} ", 'Narrator ').\
            replace(f"{given_name} {maiden_name} {surname} ", 'Narrator ')
    if maiden2_name and surname:
        new_text = new_text.replace(f"{given_name} ({maiden2_name}) {surname}'s ", "Narrator's ").\
            replace(f"{given_name} {maiden2_name} {surname}'s ", "Narrator's ")
    if surname and not maiden_name and not maiden2_name:
        new_text = new_text.replace(f"{given_name} {surname}'s ", "Narrator's ").\
            replace(f"{given_name} {surname} ", 'Narrator ')
    new_text = new_text.replace(f"{given_name} ", 'Narrator ')
    return new_text
