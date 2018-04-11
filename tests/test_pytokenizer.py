import pytest
from syntaxerrors import pytokenizer
from syntaxerrors.pytoken import tokens
from syntaxerrors.error import TokenError

def tokenize(s):
    return pytokenizer.generate_tokens(s.splitlines(True) + ["\n"], 0)

def check_token_error(s, msg=None, pos=-1, line=-1):
    error = pytest.raises(TokenError, tokenize, s)
    if msg is not None:
        assert error.value.msg == msg
    if pos != -1:
        assert error.value.offset == pos
    if line != -1:
        assert error.value.lineno == line


class TestTokenizer(object):

    def test_simple(self):
        line = "a+1"
        tks = tokenize(line)
        assert tks == [
            (tokens.NAME, 'a', 1, 0, line),
            (tokens.PLUS, '+', 1, 1, line),
            (tokens.NUMBER, '1', 1, 2, line),
            (tokens.NEWLINE, '', 2, 0, '\n'),
            (tokens.NEWLINE, '', 2, 0, '\n'),
            (tokens.ENDMARKER, '', 2, 0, ''),
            ]
