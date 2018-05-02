"""Python token definitions."""

python_tokens = {}
python_opmap = {}
python_opmap_bytes = {}

tok_name = [None] * 256

def _add_tok(name, *values):
    index = len(python_tokens)
    assert index < 256
    python_tokens[name] = index
    for value in values:
        python_opmap[value] = index
        python_opmap_bytes[value.encode("ascii")] = index

_add_tok(u'ENDMARKER')
_add_tok(u'NAME')
_add_tok(u'NUMBER')
_add_tok(u'STRING')
_add_tok(u'NEWLINE')
_add_tok(u'INDENT')
_add_tok(u'DEDENT')
_add_tok(u'LPAR', u"(")
_add_tok(u'RPAR', u")")
_add_tok(u'LSQB', u"[")
_add_tok(u'RSQB', u"]")
_add_tok(u'COLON', u":")
_add_tok(u'COMMA',  u"," )
_add_tok(u'SEMI', u";" )
_add_tok(u'PLUS', u"+" )
_add_tok(u'MINUS', u"-" )
_add_tok(u'STAR', u"*" )
_add_tok(u'SLASH', u"/" )
_add_tok(u'VBAR', u"|" )
_add_tok(u'AMPER', u"&" )
_add_tok(u'LESS', u"<" )
_add_tok(u'GREATER', u">" )
_add_tok(u'EQUAL', u"=" )
_add_tok(u'DOT', u"." )
_add_tok(u'PERCENT', u"%" )
_add_tok(u'BACKQUOTE', u"`" )
_add_tok(u'LBRACE', u"{" )
_add_tok(u'RBRACE', u"}" )
_add_tok(u'EQEQUAL', u"==" )
_add_tok(u'NOTEQUAL', u"!=", u"<>" )
_add_tok(u'LESSEQUAL', u"<=" )
_add_tok(u'GREATEREQUAL', u">=" )
_add_tok(u'TILDE', u"~" )
_add_tok(u'CIRCUMFLEX', u"^" )
_add_tok(u'LEFTSHIFT', u"<<" )
_add_tok(u'RIGHTSHIFT', u">>" )
_add_tok(u'DOUBLESTAR', u"**" )
_add_tok(u'PLUSEQUAL', u"+=" )
_add_tok(u'MINEQUAL', u"-=" )
_add_tok(u'STAREQUAL', u"*=" )
_add_tok(u'SLASHEQUAL', u"/=" )
_add_tok(u'PERCENTEQUAL', u"%=" )
_add_tok(u'AMPEREQUAL', u"&=" )
_add_tok(u'VBAREQUAL', u"|=" )
_add_tok(u'CIRCUMFLEXEQUAL', u"^=" )
_add_tok(u'LEFTSHIFTEQUAL', u"<<=" )
_add_tok(u'RIGHTSHIFTEQUAL', u">>=" )
_add_tok(u'DOUBLESTAREQUAL', u"**=" )
_add_tok(u'DOUBLESLASH', u"//" )
_add_tok(u'DOUBLESLASHEQUAL', u"//=" )
_add_tok(u'AT', u"@" )
_add_tok(u'OP')
_add_tok(u'ERRORTOKEN')

# extra PyPy-specific tokens
_add_tok(u"COMMENT")
_add_tok(u"NL")

# extra recovery-specific tokens
# those are never produced by the tokenizer, but the recovery algorithm can
# insert it
_add_tok(u"FAKESUITESTART") # behaves like: if 1: NEWLINE
_add_tok(u"FAKESUITE") # behaves like: INDENT pass DEDENT

del _add_tok

class _Tokens(object):
    pass
for name, idx in python_tokens.items():
    setattr(_Tokens, name, idx)
    tok_name[idx] = name
tokens = _Tokens()

del _Tokens, name
