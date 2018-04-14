from syntaxerrors.automata import DFA, NonGreedyDFA, DEFAULT

def test_states():
    d = DFA([{b"\x00": 1}, {b"\x01": 0}], [False, True])
    assert d.states == b"\x01\xff\xff\x00"
    assert d.defaults == b"\xff\xff"
    assert d.max_char == 2

    d = DFA([{b"\x00": 1}, {DEFAULT: 0}], [False, True])
    assert d.states == b"\x01\x00"
    assert d.defaults == b"\xff\x00"
    assert d.max_char == 1

def test_recognize():
    d = DFA([{b"a": 1}, {b"b": 0}], [False, True])
    assert d.recognize(b"ababab") == 5
    assert d.recognize(b"c") == -1

    d = DFA([{b"a": 1}, {DEFAULT: 0}], [False, True])
    assert d.recognize(b"a,a?ab") == 5
    assert d.recognize(b"c") == -1

    d = NonGreedyDFA([{b"a": 1}, {b"b": 0}], [False, True])
    assert d.recognize(b"ababab") == 1
    assert d.recognize(b"c") == -1

    d = NonGreedyDFA([{b"a": 1}, {DEFAULT: 0}], [False, True])
    assert d.recognize(b"a,a?ab") == 1
    assert d.recognize(b"c") == -1
