import pytest
from syntaxerrors import pytokenizer
from syntaxerrors.pytoken import tokens
from syntaxerrors.parser import Token
from syntaxerrors.error import TokenError

def tokenize(s):
    return pytokenizer.generate_tokens(s.splitlines(True) + [b"\n"], 0)

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
        line = b"a+1"
        uniline = u"a+1"
        tks = tokenize(line)
        assert tks == [
            Token(tokens.NAME, u'a', 1, 0, uniline),
            Token(tokens.PLUS, u'+', 1, 1, uniline),
            Token(tokens.NUMBER, u'1', 1, 2, uniline),
            Token(tokens.NEWLINE, u'\n', 2, 0, u'\n'),
            Token(tokens.NEWLINE, u'\n', 2, 0, u'\n'),
            Token(tokens.ENDMARKER, u'', 2, 0, u''),
            ]

    def test_bug_python3(self):
        line = b"   \\\n  \t\\\nfrom __future__ import with_statement\n"
        tks = tokenize(line)
        line1 = u'   \\\n'
        line2 = u'from __future__ import with_statement\n'
        line3 = u''
        line4 = u'\n'
        assert tks == [
            Token(tokens.INDENT, u'   ', 1, 0, line1),
            Token(tokens.NAME, u'from', 3, 0, line2),
            Token(tokens.NAME, u'__future__', 3, 5, line2),
            Token(tokens.NAME, u'import', 3, 16, line2),
            Token(tokens.NAME, u'with_statement', 3, 23, line2),
            Token(tokens.NEWLINE, u'', 3, 37, line2),
            Token(tokens.DEDENT, u'', 4, 0, line3),
            Token(tokens.NEWLINE, u'\n', 4, 0, line4),
            Token(tokens.ENDMARKER, u'', 4, 0, line3)
        ]


    def test_error_parenthesis(self):
        for paren in u"([{":
            check_token_error(paren.encode("utf-8") + b"1 + 2",
                              "parenthesis is never closed",
                              1)

        for paren in u")]}":
            check_token_error(b"1 + 2" + paren.encode("utf-8"),
                              "unmatched '%s'" % (paren, ),
                              6)

        for i, opening in enumerate("([{"):
            for j, closing in enumerate(")]}"):
                if i == j:
                    continue
                check_token_error(opening.encode("utf-8") + b"1\n" + closing.encode("utf-8"),
                        "closing parenthesis '%s' does not match opening parenthesis '%s' on line 1" % (closing, opening),
                        pos=1, line=2)
                check_token_error(opening.encode("utf-8") + b"1" + closing.encode("utf-8"),
                        "closing parenthesis '%s' does not match opening parenthesis '%s'" % (closing, opening),
                        pos=3, line=1)
                check_token_error(opening.encode("utf-8") + closing.encode("utf-8"),
                        "closing parenthesis '%s' does not match opening parenthesis '%s'" % (closing, opening),
                        pos=2, line=1)


    def test_unknown_char(self):
        check_token_error(b"?", "Unknown character", 1)

    def test_eol_string(self):
        check_token_error(b"x = 'a", pos=5, line=1)

    def test_eof_triple_quoted(self):
        check_token_error(b"'''", pos=1, line=1)
