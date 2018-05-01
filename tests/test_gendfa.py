from syntaxerrors.automata import DFA, DEFAULT
from syntaxerrors.genpytokenize import output

def test_states():
    states = [{b"\x00": 1}, {b"\x01": 0}]
    d = DFA(states[:], [False, True])
    assert output('test', DFA, d, states) == """\
accepts = [False, True]
states = [
    # 0
    {b'\\x00': 1},
    # 1
    {b'\\x01': 0},
    ]
test = automata.DFA(states, accepts)
"""
