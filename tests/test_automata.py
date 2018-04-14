from syntaxerrors.automata import DFA, DEFAULT

def test_states():
    d = DFA([{b"\x00": 1}, {b"\x01": 0}], [False, True])
    assert d.states == b"\x01\xff\xff\x00"
    assert d.defaults == b"\xff\xff"
    assert d.max_char == 2

    d = DFA([{b"\x00": 1}, {DEFAULT: 0}], [False, True])
    assert d.states == b"\x01\x00"
    assert d.defaults == b"\xff\x00"
    assert d.max_char == 1
