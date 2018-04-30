import os
import io
from syntaxerrors import parser, pytoken
from syntaxerrors.pytoken import tokens


class PythonGrammar(parser.Grammar):

    KEYWORD_TOKEN = tokens.NAME
    TOKENS = pytoken.python_tokens
    OPERATOR_MAP = pytoken.python_opmap

    never_generate_as_fake = {
        tokens.ENDMARKER,
        tokens.INDENT,
        tokens.DEDENT,
    }

    never_delete = {
        tokens.ENDMARKER,
        tokens.INDENT,
        tokens.DEDENT,
        tokens.NEWLINE,
    }


def _get_python_grammar():
    from syntaxerrors import metaparser
    here = os.path.dirname(__file__)
    fp = io.open(os.path.join(here, "data", "Grammar2.7"), "rb")
    try:
        gram_source = fp.read()
    finally:
        fp.close()
    pgen = metaparser.ParserGenerator(gram_source)
    return pgen.build_grammar(PythonGrammar)


python_grammar = _get_python_grammar()
python_grammar_no_print = python_grammar.shared_copy()
python_grammar_no_print.keyword_ids = python_grammar_no_print.keyword_ids.copy()
del python_grammar_no_print.keyword_ids["print"]


class _Symbols(object):
    pass
rev_lookup = {}
for sym_name, idx in python_grammar.symbol_ids.items():
    setattr(_Symbols, sym_name, idx)
    rev_lookup[idx] = sym_name
syms = _Symbols()
syms._rev_lookup = rev_lookup # for debugging

del _get_python_grammar,  sym_name, idx
