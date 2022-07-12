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
