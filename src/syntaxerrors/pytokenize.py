# ______________________________________________________________________
"""Module pytokenize

This is a modified version of Ka-Ping Yee's tokenize module found in the
Python standard library.

The primary modification is the removal of the tokenizer's dependence on the
standard Python regular expression module, which is written in C.  The regular
expressions have been replaced with hand built DFA's using the
basil.util.automata module.

"""
# ______________________________________________________________________

from syntaxerrors import automata
from syntaxerrors.dfa_generated import *

__all__ = [ "tokenize" ]

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
