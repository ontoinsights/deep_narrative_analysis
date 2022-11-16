# Patterns used in spaCy matching
# Called by nlp.py

from dna.utilities_and_language_specific import family_members, plural_family_members

# spaCy pattern matching for family names
DEP = 'DEP'
ENT_TYPE = 'ENT_TYPE'
LEFT_ID = 'LEFT_ID'
ORTH = 'ORTH'
POS = 'POS'
RIGHT_ID = 'RIGHT_ID'
RIGHT_ATTRS = 'RIGHT_ATTRS'
REL_OP = 'REL_OP'

# For example, match 'her sister, Beatrice' or 'her sister, Beatrice Mary'
member_name_pattern = [
    {RIGHT_ID: 'family_member', RIGHT_ATTRS: {ORTH: {'IN': list(family_members.keys())}}},
    {LEFT_ID: 'family_member', REL_OP: '>',
     RIGHT_ID: 'proper_name', RIGHT_ATTRS: {DEP: 'appos', POS: 'PROPN'}}]

# For example, match 'her sisters, Beatrice and Susan'
members_names_pattern = [
    {RIGHT_ID: 'family_members', RIGHT_ATTRS: {ORTH: {'IN': plural_family_members}}},
    {LEFT_ID: 'family_members', REL_OP: '>',
     RIGHT_ID: 'proper_name', RIGHT_ATTRS: {DEP: 'appos', POS: 'PROPN'}}]

# For example, match 'Beatrice, her sister'
name_member_pattern = [
    {RIGHT_ID: 'proper_name', RIGHT_ATTRS: {POS: 'PROPN'}},
    {LEFT_ID: 'proper_name', REL_OP: '>',
     RIGHT_ID: 'family_member', RIGHT_ATTRS: {DEP: 'appos', ORTH: {'IN': list(family_members.keys())}}}]

# For example, match 'Beatrice and Susan (her sisters)'
names_members_pattern = [
    {RIGHT_ID: 'proper_name', RIGHT_ATTRS: {POS: 'PROPN'}},
    {LEFT_ID: 'proper_name', REL_OP: '>',
     RIGHT_ID: 'family_members', RIGHT_ATTRS: {DEP: 'appos', ORTH: {'IN': plural_family_members}}}]

# For example, match 'her brother is Bob Smith.'
member_verb_name_pattern = [
    {RIGHT_ID: 'verb_be', RIGHT_ATTRS: {DEP: 'ROOT', 'LEMMA': 'be'}},
    {LEFT_ID: 'verb_be', REL_OP: '>',
     RIGHT_ID: 'family_member', RIGHT_ATTRS: {DEP: 'nsubj', ORTH: {'IN': list(family_members.keys())}}},
    {LEFT_ID: 'verb_be', REL_OP: '>',
     RIGHT_ID: 'proper_name', RIGHT_ATTRS: {DEP: 'attr', POS: 'PROPN'}}]

# For example, match 'her brothers are Bob, George and Paul Smith.'
members_verb_names_pattern = [
    {RIGHT_ID: 'verb_be', RIGHT_ATTRS: {DEP: 'ROOT', 'LEMMA': 'be'}},
    {LEFT_ID: 'verb_be', REL_OP: '>',
     RIGHT_ID: 'family_members', RIGHT_ATTRS: {DEP: 'nsubj', ORTH: {'IN': plural_family_members}}},
    {LEFT_ID: 'verb_be', REL_OP: '>',
     RIGHT_ID: 'proper_name', RIGHT_ATTRS: {DEP: 'attr', POS: 'PROPN'}}]

# For example, match 'Bob Jones is her brother'
name_verb_member_pattern = [
    {RIGHT_ID: 'verb_be', RIGHT_ATTRS: {DEP: 'ROOT', 'LEMMA': 'be'}},
    {LEFT_ID: 'verb_be', REL_OP: '>',
     RIGHT_ID: 'family_member', RIGHT_ATTRS: {DEP: 'attr', ORTH: {'IN': list(family_members.keys())}}},
    {LEFT_ID: 'verb_be', REL_OP: '>',
     RIGHT_ID: 'proper_name', RIGHT_ATTRS: {DEP: 'nsubj', POS: 'PROPN'}}]

# For example, match 'Bob and George Smith are her brothers'
names_verb_members_pattern = [
    {RIGHT_ID: 'verb_be', RIGHT_ATTRS: {DEP: 'ROOT', 'LEMMA': 'be'}},
    {LEFT_ID: 'verb_be', REL_OP: '>',
     RIGHT_ID: 'family_members', RIGHT_ATTRS: {DEP: 'attr', ORTH: {'IN': plural_family_members}}},
    {LEFT_ID: 'verb_be', REL_OP: '>',
     RIGHT_ID: 'proper_name', RIGHT_ATTRS: {DEP: 'nsubj', POS: 'PROPN'}}]
