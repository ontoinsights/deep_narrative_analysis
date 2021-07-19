# Patterns used in spaCy matching

# "born ... on ... in ..."
born_date_pattern = [
  # anchor token: born
  {
    'RIGHT_ID': 'born1',
    'RIGHT_ATTRS': {'ORTH': 'born'}
  },
  # subject should be 'I'
  {
    'LEFT_ID': 'born1',
    'REL_OP': '>',
    'RIGHT_ID': 'I_born1',
    'RIGHT_ATTRS': {'ORTH': 'I'}
  },
  # date follows "born"
  {
    'LEFT_ID': 'born1',
    'REL_OP': '>>',
    'RIGHT_ID': 'born_date',
    'RIGHT_ATTRS': {'ENT_TYPE': 'DATE'}
  }
]

born_place_pattern = [
  # anchor token: born
  {
    'RIGHT_ID': 'born2',
    'RIGHT_ATTRS': {'ORTH': 'born'}
  },
  # subject should be 'I'
  {
    'LEFT_ID': 'born2',
    'REL_OP': '>',
    'RIGHT_ID': 'I_born2',
    'RIGHT_ATTRS': {'ORTH': 'I'}
  },
  # place follows "born"
  {
    'LEFT_ID': 'born2',
    'REL_OP': '>>',
    'RIGHT_ID': 'born_place',
    'RIGHT_ATTRS': {'ENT_TYPE': {'IN': ['GPE', 'LOC']}}
  }
]

family_member_name_pattern = [
  # anchor token: family relation
  {
    'RIGHT_ID': 'family_member',
    'RIGHT_ATTRS': {'ORTH': {'IN': ['sister', 'brother', 'mother', 'father', 'cousin',
                                    'grandmother', 'grandfather', 'aunt', 'uncle']}}
  },
  # Relative's name follows the relationship
  {
    'LEFT_ID': 'family_member',
    'REL_OP': '>',
    'RIGHT_ID': 'proper_name',
    'RIGHT_ATTRS': {'DEP': 'appos', 'POS': 'PROPN'}
  },
  # Entity holding the relationship should be 'my'
  # TODO: Should we collect other relationships such as "John's sister, Beatrice"?
  {
    'LEFT_ID': 'family_member',
    'REL_OP': '>',
    'RIGHT_ID': 'possessive',
    'RIGHT_ATTRS': {'DEP': 'pos', 'ORTH': {'IN': ['My', 'my']}}
  }
]
