
transforms = [
    {'type': 'combine', 'name': 'addr_state', 'payload': ['CA', 'TX']},
    {'type': 'drop', 'name': 'addr_state', 'payload': ['IA', 'ME']}
]
