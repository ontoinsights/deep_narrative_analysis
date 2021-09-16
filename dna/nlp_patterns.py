# Patterns used in spaCy matching
# Called by nlp.py

from utilities import family_members

DEP = 'DEP'
ENT_TYPE = 'ENT_TYPE'
LEFT_ID = 'LEFT_ID'
ORTH = 'ORTH'
RIGHT_ID = 'RIGHT_ID'
RIGHT_ATTRS = 'RIGHT_ATTRS'
REL_OP = 'REL_OP'

# "born ... on ... in ..."
born_date_pattern = [
  # anchor token: born
  {
    RIGHT_ID: 'born1',
    RIGHT_ATTRS: {ORTH: 'born'}
  },
  # subject should be 'I'
  {
    LEFT_ID: 'born1',
    REL_OP: '>',
    RIGHT_ID: 'I_born1',
    RIGHT_ATTRS: {ORTH: {'IN': ['I', 'Narrator']}}
  },
  # date follows "born"
  {
    LEFT_ID: 'born1',
    REL_OP: '>>',
    RIGHT_ID: 'born_date',
    RIGHT_ATTRS: {ENT_TYPE: 'DATE'}
  }
]

born_place_pattern = [
  # anchor token: born
  {
    RIGHT_ID: 'born2',
    RIGHT_ATTRS: {ORTH: 'born'}
  },
  # subject should be 'I'
  {
    LEFT_ID: 'born2',
    REL_OP: '>',
    RIGHT_ID: 'I_born2',
    RIGHT_ATTRS: {ORTH: {'IN': ['I', 'Narrator']}}
  },
  # place follows "born"
  {
    LEFT_ID: 'born2',
    REL_OP: '>>',
    RIGHT_ID: 'born_place',
    RIGHT_ATTRS: {ENT_TYPE: {'IN': ['GPE', 'LOC']}}
  }
]

family_member_name_pattern = [
  # anchor token: family relation
  {
    RIGHT_ID: 'family_member',
    RIGHT_ATTRS: {ORTH: {'IN': list(family_members.keys())}}
  },
  # Relative's name follows the relationship
  {
    LEFT_ID: 'family_member',
    REL_OP: '>',
    RIGHT_ID: 'proper_name',
    RIGHT_ATTRS: {DEP: 'appos', 'POS': 'PROPN'}
  }
]
