# ______________________________________________________________________
"""Module pytokenize

THIS FILE WAS COPIED FROM pypy/module/parser/pytokenize.py AND ADAPTED
TO BE ANNOTABLE (Mainly made lists homogeneous)

This is a modified version of Ka-Ping Yee's tokenize module found in the
Python standard library.

The primary modification is the removal of the tokenizer's dependence on the
standard Python regular expression module, which is written in C.  The regular
expressions have been replaced with hand built DFA's using the
basil.util.automata module.

$Id: pytokenize.py,v 1.3 2003/10/03 16:31:53 jriehl Exp $
"""
# ______________________________________________________________________

from syntaxerrors import automata

__all__ = [ "tokenize" ]

# ______________________________________________________________________
# Automatically generated DFA's

accepts = [True, True, True, True, True, True, True, True,
           True, True, False, True, True, True, True, False,
           False, False, True, False, False, True, False,
           False, True, False, True, False, True, False,
           False, True, False, False, True, True, True,
           False, False, True, False, False, False, True]
states = [
    # 0
    {b'\t': 0, b'\n': 13, b'\x0c': 0,
     b'\r': 14, b' ': 0, b'!': 10,
     b'"': 16, b'#': 18, b'%': 12,
     b'&': 12, b"'": 15, b'(': 13,
     b')': 13, b'*': 7, b'+': 12,
     b',': 13, b'-': 12, b'.': 6,
     b'/': 11, b'0': 4, b'1': 5, b'2': 5,
     b'3': 5, b'4': 5, b'5': 5, b'6': 5,
     b'7': 5, b'8': 5, b'9': 5, b':': 13,
     b';': 13, b'<': 9, b'=': 12,
     b'>': 8, b'@': 13, b'A': 1, b'B': 2,
     b'C': 1, b'D': 1, b'E': 1, b'F': 1,
     b'G': 1, b'H': 1, b'I': 1, b'J': 1,
     b'K': 1, b'L': 1, b'M': 1, b'N': 1,
     b'O': 1, b'P': 1, b'Q': 1, b'R': 3,
     b'S': 1, b'T': 1, b'U': 2, b'V': 1,
     b'W': 1, b'X': 1, b'Y': 1, b'Z': 1,
     b'[': 13, b'\\': 17, b']': 13,
     b'^': 12, b'_': 1, b'`': 13,
     b'a': 1, b'b': 2, b'c': 1, b'd': 1,
     b'e': 1, b'f': 1, b'g': 1, b'h': 1,
     b'i': 1, b'j': 1, b'k': 1, b'l': 1,
     b'm': 1, b'n': 1, b'o': 1, b'p': 1,
     b'q': 1, b'r': 3, b's': 1, b't': 1,
     b'u': 2, b'v': 1, b'w': 1, b'x': 1,
     b'y': 1, b'z': 1, b'{': 13,
     b'|': 12, b'}': 13, b'~': 13},
    # 1
    {b'0': 1, b'1': 1, b'2': 1, b'3': 1,
     b'4': 1, b'5': 1, b'6': 1, b'7': 1,
     b'8': 1, b'9': 1, b'A': 1, b'B': 1,
     b'C': 1, b'D': 1, b'E': 1, b'F': 1,
     b'G': 1, b'H': 1, b'I': 1, b'J': 1,
     b'K': 1, b'L': 1, b'M': 1, b'N': 1,
     b'O': 1, b'P': 1, b'Q': 1, b'R': 1,
     b'S': 1, b'T': 1, b'U': 1, b'V': 1,
     b'W': 1, b'X': 1, b'Y': 1, b'Z': 1,
     b'_': 1, b'a': 1, b'b': 1, b'c': 1,
     b'd': 1, b'e': 1, b'f': 1, b'g': 1,
     b'h': 1, b'i': 1, b'j': 1, b'k': 1,
     b'l': 1, b'm': 1, b'n': 1, b'o': 1,
     b'p': 1, b'q': 1, b'r': 1, b's': 1,
     b't': 1, b'u': 1, b'v': 1, b'w': 1,
     b'x': 1, b'y': 1, b'z': 1},
    # 2
    {b'"': 16, b"'": 15, b'0': 1,
     b'1': 1, b'2': 1, b'3': 1, b'4': 1,
     b'5': 1, b'6': 1, b'7': 1, b'8': 1,
     b'9': 1, b'A': 1, b'B': 1, b'C': 1,
     b'D': 1, b'E': 1, b'F': 1, b'G': 1,
     b'H': 1, b'I': 1, b'J': 1, b'K': 1,
     b'L': 1, b'M': 1, b'N': 1, b'O': 1,
     b'P': 1, b'Q': 1, b'R': 3, b'S': 1,
     b'T': 1, b'U': 1, b'V': 1, b'W': 1,
     b'X': 1, b'Y': 1, b'Z': 1, b'_': 1,
     b'a': 1, b'b': 1, b'c': 1, b'd': 1,
     b'e': 1, b'f': 1, b'g': 1, b'h': 1,
     b'i': 1, b'j': 1, b'k': 1, b'l': 1,
     b'm': 1, b'n': 1, b'o': 1, b'p': 1,
     b'q': 1, b'r': 3, b's': 1, b't': 1,
     b'u': 1, b'v': 1, b'w': 1, b'x': 1,
     b'y': 1, b'z': 1},
    # 3
    {b'"': 16, b"'": 15, b'0': 1,
     b'1': 1, b'2': 1, b'3': 1, b'4': 1,
     b'5': 1, b'6': 1, b'7': 1, b'8': 1,
     b'9': 1, b'A': 1, b'B': 1, b'C': 1,
     b'D': 1, b'E': 1, b'F': 1, b'G': 1,
     b'H': 1, b'I': 1, b'J': 1, b'K': 1,
     b'L': 1, b'M': 1, b'N': 1, b'O': 1,
     b'P': 1, b'Q': 1, b'R': 1, b'S': 1,
     b'T': 1, b'U': 1, b'V': 1, b'W': 1,
     b'X': 1, b'Y': 1, b'Z': 1, b'_': 1,
     b'a': 1, b'b': 1, b'c': 1, b'd': 1,
     b'e': 1, b'f': 1, b'g': 1, b'h': 1,
     b'i': 1, b'j': 1, b'k': 1, b'l': 1,
     b'm': 1, b'n': 1, b'o': 1, b'p': 1,
     b'q': 1, b'r': 1, b's': 1, b't': 1,
     b'u': 1, b'v': 1, b'w': 1, b'x': 1,
     b'y': 1, b'z': 1},
    # 4
    {b'.': 24, b'0': 21, b'1': 21,
     b'2': 21, b'3': 21, b'4': 21,
     b'5': 21, b'6': 21, b'7': 21,
     b'8': 23, b'9': 23, b'B': 22,
     b'E': 25, b'J': 13, b'L': 13,
     b'O': 20, b'X': 19, b'b': 22,
     b'e': 25, b'j': 13, b'l': 13,
     b'o': 20, b'x': 19},
    # 5
    {b'.': 24, b'0': 5, b'1': 5, b'2': 5,
     b'3': 5, b'4': 5, b'5': 5, b'6': 5,
     b'7': 5, b'8': 5, b'9': 5, b'E': 25,
     b'J': 13, b'L': 13, b'e': 25,
     b'j': 13, b'l': 13},
    # 6
    {b'0': 26, b'1': 26, b'2': 26,
     b'3': 26, b'4': 26, b'5': 26,
     b'6': 26, b'7': 26, b'8': 26,
     b'9': 26},
    # 7
    {b'*': 12, b'=': 13},
    # 8
    {b'=': 13, b'>': 12},
    # 9
    {b'<': 12, b'=': 13, b'>': 13},
    # 10
    {b'=': 13},
    # 11
    {b'/': 12, b'=': 13},
    # 12
    {b'=': 13},
    # 13
    {},
    # 14
    {b'\n': 13},
    # 15
    {automata.DEFAULT: 30, b'\n': 27,
     b'\r': 27, b"'": 28, b'\\': 29},
    # 16
    {automata.DEFAULT: 33, b'\n': 27,
     b'\r': 27, b'"': 31, b'\\': 32},
    # 17
    {b'\n': 13, b'\r': 14},
    # 18
    {automata.DEFAULT: 18, b'\n': 27, b'\r': 27},
    # 19
    {b'0': 34, b'1': 34, b'2': 34,
     b'3': 34, b'4': 34, b'5': 34,
     b'6': 34, b'7': 34, b'8': 34,
     b'9': 34, b'A': 34, b'B': 34,
     b'C': 34, b'D': 34, b'E': 34,
     b'F': 34, b'a': 34, b'b': 34,
     b'c': 34, b'd': 34, b'e': 34,
     b'f': 34},
    # 20
    {b'0': 35, b'1': 35, b'2': 35,
     b'3': 35, b'4': 35, b'5': 35,
     b'6': 35, b'7': 35},
    # 21
    {b'.': 24, b'0': 21, b'1': 21,
     b'2': 21, b'3': 21, b'4': 21,
     b'5': 21, b'6': 21, b'7': 21,
     b'8': 23, b'9': 23, b'E': 25,
     b'J': 13, b'L': 13, b'e': 25,
     b'j': 13, b'l': 13},
    # 22
    {b'0': 36, b'1': 36},
    # 23
    {b'.': 24, b'0': 23, b'1': 23,
     b'2': 23, b'3': 23, b'4': 23,
     b'5': 23, b'6': 23, b'7': 23,
     b'8': 23, b'9': 23, b'E': 25,
     b'J': 13, b'e': 25, b'j': 13},
    # 24
    {b'0': 24, b'1': 24, b'2': 24,
     b'3': 24, b'4': 24, b'5': 24,
     b'6': 24, b'7': 24, b'8': 24,
     b'9': 24, b'E': 37, b'J': 13,
     b'e': 37, b'j': 13},
    # 25
    {b'+': 38, b'-': 38, b'0': 39,
     b'1': 39, b'2': 39, b'3': 39,
     b'4': 39, b'5': 39, b'6': 39,
     b'7': 39, b'8': 39, b'9': 39},
    # 26
    {b'0': 26, b'1': 26, b'2': 26,
     b'3': 26, b'4': 26, b'5': 26,
     b'6': 26, b'7': 26, b'8': 26,
     b'9': 26, b'E': 37, b'J': 13,
     b'e': 37, b'j': 13},
    # 27
    {},
    # 28
    {b"'": 13},
    # 29
    {automata.DEFAULT: 40, b'\n': 13, b'\r': 14},
    # 30
    {automata.DEFAULT: 30, b'\n': 27,
     b'\r': 27, b"'": 13, b'\\': 29},
    # 31
    {b'"': 13},
    # 32
    {automata.DEFAULT: 41, b'\n': 13, b'\r': 14},
    # 33
    {automata.DEFAULT: 33, b'\n': 27,
     b'\r': 27, b'"': 13, b'\\': 32},
    # 34
    {b'0': 34, b'1': 34, b'2': 34,
     b'3': 34, b'4': 34, b'5': 34,
     b'6': 34, b'7': 34, b'8': 34,
     b'9': 34, b'A': 34, b'B': 34,
     b'C': 34, b'D': 34, b'E': 34,
     b'F': 34, b'L': 13, b'a': 34,
     b'b': 34, b'c': 34, b'd': 34,
     b'e': 34, b'f': 34, b'l': 13},
    # 35
    {b'0': 35, b'1': 35, b'2': 35,
     b'3': 35, b'4': 35, b'5': 35,
     b'6': 35, b'7': 35, b'L': 13,
     b'l': 13},
    # 36
    {b'0': 36, b'1': 36, b'L': 13, b'l': 13},
    # 37
    {b'+': 42, b'-': 42, b'0': 43,
     b'1': 43, b'2': 43, b'3': 43,
     b'4': 43, b'5': 43, b'6': 43,
     b'7': 43, b'8': 43, b'9': 43},
    # 38
    {b'0': 39, b'1': 39, b'2': 39,
     b'3': 39, b'4': 39, b'5': 39,
     b'6': 39, b'7': 39, b'8': 39,
     b'9': 39},
    # 39
    {b'0': 39, b'1': 39, b'2': 39,
     b'3': 39, b'4': 39, b'5': 39,
     b'6': 39, b'7': 39, b'8': 39,
     b'9': 39, b'J': 13, b'j': 13},
    # 40
    {automata.DEFAULT: 40, b'\n': 27,
     b'\r': 27, b"'": 13, b'\\': 29},
    # 41
    {automata.DEFAULT: 41, b'\n': 27,
     b'\r': 27, b'"': 13, b'\\': 32},
    # 42
    {b'0': 43, b'1': 43, b'2': 43,
     b'3': 43, b'4': 43, b'5': 43,
     b'6': 43, b'7': 43, b'8': 43,
     b'9': 43},
    # 43
    {b'0': 43, b'1': 43, b'2': 43,
     b'3': 43, b'4': 43, b'5': 43,
     b'6': 43, b'7': 43, b'8': 43,
     b'9': 43, b'J': 13, b'j': 13},
    ]
pseudoDFA = automata.DFA(states, accepts)

accepts = [False, False, False, False, False, True]
states = [
    # 0
    {automata.DEFAULT: 0, b'"': 1, b'\\': 2},
    # 1
    {automata.DEFAULT: 4, b'"': 3, b'\\': 2},
    # 2
    {automata.DEFAULT: 4},
    # 3
    {automata.DEFAULT: 4, b'"': 5, b'\\': 2},
    # 4
    {automata.DEFAULT: 4, b'"': 1, b'\\': 2},
    # 5
    {automata.DEFAULT: 4, b'"': 5, b'\\': 2},
    ]
double3DFA = automata.NonGreedyDFA(states, accepts)

accepts = [False, False, False, False, False, True]
states = [
    # 0
    {automata.DEFAULT: 0, b"'": 1, b'\\': 2},
    # 1
    {automata.DEFAULT: 4, b"'": 3, b'\\': 2},
    # 2
    {automata.DEFAULT: 4},
    # 3
    {automata.DEFAULT: 4, b"'": 5, b'\\': 2},
    # 4
    {automata.DEFAULT: 4, b"'": 1, b'\\': 2},
    # 5
    {automata.DEFAULT: 4, b"'": 5, b'\\': 2},
    ]
single3DFA = automata.NonGreedyDFA(states, accepts)

accepts = [False, True, False, False]
states = [
    # 0
    {automata.DEFAULT: 0, b"'": 1, b'\\': 2},
    # 1
    {},
    # 2
    {automata.DEFAULT: 3},
    # 3
    {automata.DEFAULT: 3, b"'": 1, b'\\': 2},
    ]
singleDFA = automata.DFA(states, accepts)

accepts = [False, True, False, False]
states = [
    # 0
    {automata.DEFAULT: 0, b'"': 1, b'\\': 2},
    # 1
    {},
    # 2
    {automata.DEFAULT: 3},
    # 3
    {automata.DEFAULT: 3, b'"': 1, b'\\': 2},
    ]
doubleDFA = automata.DFA(states, accepts)

#_______________________________________________________________________
# End of automatically generated DFA's

endDFAs = {b"'" : singleDFA,
           b'"' : doubleDFA,
           b'r' : None,
           b'R' : None,
           b'u' : None,
           b'U' : None,
           b'b' : None,
           b'B' : None}

for uniPrefix in (b"", b"u", b"U", b"b", b"B"):
    for rawPrefix in (b"", b"r", b"R"):
        prefix = uniPrefix + rawPrefix
        endDFAs[prefix + b"'''"] = single3DFA
        endDFAs[prefix + b'"""'] = double3DFA

whiteSpaceStatesAccepts = [True]
whiteSpaceStates = [{b'\t': 0, b' ': 0, b'\x0c': 0}]
whiteSpaceDFA = automata.DFA(whiteSpaceStates, whiteSpaceStatesAccepts)

# ______________________________________________________________________
# COPIED:

triple_quoted = {}
for t in (b"'''", b'"""',
          b"r'''", b'r"""', b"R'''", b'R"""',
          b"u'''", b'u"""', b"U'''", b'U"""',
          b"b'''", b'b"""', b"B'''", b'B"""',
          b"ur'''", b'ur"""', b"Ur'''", b'Ur"""',
          b"uR'''", b'uR"""', b"UR'''", b'UR"""',
          b"br'''", b'br"""', b"Br'''", b'Br"""',
          b"bR'''", b'bR"""', b"BR'''", b'BR"""'):
    triple_quoted[t] = t
single_quoted = {}
for t in (b"'", b'"',
          b"r'", b'r"', b"R'", b'R"',
          b"u'", b'u"', b"U'", b'U"',
          b"b'", b'b"', b"B'", b'B"',
          b"ur'", b'ur"', b"Ur'", b'Ur"',
          b"uR'", b'uR"', b"UR'", b'UR"',
          b"br'", b'br"', b"Br'", b'Br"',
          b"bR'", b'bR"', b"BR'", b'BR"'):
    single_quoted[t] = t

tabsize = 8

# PYPY MODIFICATION: removed TokenError class as it's not needed here

# PYPY MODIFICATION: removed StopTokenizing class as it's not needed here

# PYPY MODIFICATION: removed printtoken() as it's not needed here

# PYPY MODIFICATION: removed tokenize() as it's not needed here

# PYPY MODIFICATION: removed tokenize_loop() as it's not needed here

# PYPY MODIFICATION: removed generate_tokens() as it was copied / modified
#                    in pythonlexer.py

# PYPY MODIFICATION: removed main() as it's not needed here

# ______________________________________________________________________
# End of pytokenize.py

