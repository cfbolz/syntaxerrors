import six

import pytest
import os
import glob
import tokenize
import token
from syntaxerrors.metaparser import ParserGenerator, PgenError
from syntaxerrors import parser, pytoken


class MyGrammar(parser.Grammar):
    TOKENS = dict(pytoken.tokens.__class__.__dict__)
    OPERATOR_MAP = {
        "+" : token.OP,
        "-" : token.OP,
        "*" : token.OP,
        "(" : token.OP,
        ")" : token.OP,
        "=" : token.OP,
        }
    KEYWORD_TOKEN = token.NAME


class TestParserGenerator:

    def gram_for(self, grammar_source):
        assert isinstance(grammar_source, bytes)
        p = ParserGenerator(grammar_source + b"\n")
        return p.build_grammar(MyGrammar)

    def test_multiple_rules(self):
        g = self.gram_for(b"foo: NAME bar\nbar: STRING")
        assert len(g.dfas) == 2
        assert g.start == g.symbol_ids["foo"]

    def test_simple(self):
        g = self.gram_for(b"eval: NAME\n")
        assert len(g.dfas) == 1
        eval_sym = g.symbol_ids["eval"]
        assert g.start == eval_sym
        dfa = g.dfas[eval_sym - 256]
        assert dfa.states == [([(1, 1)], False), ([], True)]
        assert g.labels[0] == 0

    def test_load_python_grammars(self):
        from syntaxerrors.pygram import PythonGrammar
        gram_pat = os.path.join(os.path.dirname(__file__), "..", "data",
                                "Grammar*")
        for gram_file in glob.glob(gram_pat):
            fp = open(gram_file, "r")
            try:
                ParserGenerator(fp.read()).build_grammar(PythonGrammar)
            finally:
                fp.close()

    def test_items(self):
        g = self.gram_for(b"foo: NAME STRING OP '+'")
        assert len(g.dfas) == 1
        states = g.dfas[g.symbol_ids["foo"] - 256].states
        last = states[0][0][0][1]
        for state in states[1:-1]:
            assert last < state[0][0][1]
            last = state[0][0][1]

    def test_alternatives(self):
        g = self.gram_for(b"foo: STRING | OP")
        assert len(g.dfas) == 1

    def test_optional(self):
        g = self.gram_for(b"foo: [NAME]")

    def test_grouping(self):
        g = self.gram_for(b"foo: (NAME | STRING) OP")

    def test_keyword(self):
        g = self.gram_for(b"foo: 'some_keyword' 'for'")
        assert len(g.keyword_ids) == 2
        assert len(g.token_ids) == 0

    def test_token(self):
        g = self.gram_for(b"foo: NAME")
        assert len(g.token_ids) == 1

    def test_operator(self):
        g = self.gram_for(b"add: NUMBER '+' NUMBER")
        assert len(g.keyword_ids) == 0
        assert len(g.token_ids) == 2

        exc = pytest.raises(PgenError, self.gram_for, b"add: '/'").value
        assert str(exc) == "no such operator: /"

    def test_symbol(self):
        g = self.gram_for(b"foo: some_other_rule\nsome_other_rule: NAME")
        assert len(g.dfas) == 2
        assert len(g.labels) == 3

        exc = pytest.raises(PgenError, self.gram_for, b"foo: no_rule").value
        assert str(exc) == "no such rule: no_rule"

    def test_repeaters(self):
        g1 = self.gram_for(b"foo: NAME+")
        g2 = self.gram_for(b"foo: NAME*")
        assert g1.dfas != g2.dfas

        g = self.gram_for(b"foo: (NAME | STRING)*")
        g = self.gram_for(b"foo: (NAME | STRING)+")

    def test_error(self):
        exc = pytest.raises(PgenError, self.gram_for, b"hi").value
        assert str(exc) == "expected token COLON but got NEWLINE"
        assert exc.token.lineno == 1
        exc = pytest.raises(PgenError, self.gram_for, b"hi+").value
        assert str(exc) == "expected token COLON but got PLUS"
        assert exc.token.lineno == 1

    def test_comments_and_whitespace(self):
        self.gram_for(b"\n\n# comment\nrule: NAME # comment")
