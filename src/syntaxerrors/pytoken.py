"""Python token definitions."""

python_tokens = {}
python_opmap = {}

tok_name = [None] * 256

def _add_tok(name, *values):
    index = len(python_tokens)
    assert index < 256
    python_tokens[name] = index
    for value in values:
        python_opmap[value] = index

_add_tok('ENDMARKER')
_add_tok('NAME')
_add_tok('NUMBER')
_add_tok('STRING')
_add_tok('NEWLINE')
_add_tok('INDENT')
_add_tok('DEDENT')
_add_tok('LPAR', b"(")
_add_tok('RPAR', b")")
_add_tok('LSQB', b"[")
_add_tok('RSQB', b"]")
_add_tok('COLON', b":")
_add_tok('COMMA',  b"," )
_add_tok('SEMI', b";" )
_add_tok('PLUS', b"+" )
_add_tok('MINUS', b"-" )
_add_tok('STAR', b"*" )
_add_tok('SLASH', b"/" )
_add_tok('VBAR', b"|" )
_add_tok('AMPER', b"&" )
_add_tok('LESS', b"<" )
_add_tok('GREATER', b">" )
_add_tok('EQUAL', b"=" )
_add_tok('DOT', b"." )
_add_tok('PERCENT', b"%" )
_add_tok('BACKQUOTE', b"`" )
_add_tok('LBRACE', b"{" )
_add_tok('RBRACE', b"}" )
_add_tok('EQEQUAL', b"==" )
_add_tok('NOTEQUAL', b"!=", b"<>" )
_add_tok('LESSEQUAL', b"<=" )
_add_tok('GREATEREQUAL', b">=" )
_add_tok('TILDE', b"~" )
_add_tok('CIRCUMFLEX', b"^" )
_add_tok('LEFTSHIFT', b"<<" )
_add_tok('RIGHTSHIFT', b">>" )
_add_tok('DOUBLESTAR', b"**" )
_add_tok('PLUSEQUAL', b"+=" )
_add_tok('MINEQUAL', b"-=" )
_add_tok('STAREQUAL', b"*=" )
_add_tok('SLASHEQUAL', b"/=" )
_add_tok('PERCENTEQUAL', b"%=" )
_add_tok('AMPEREQUAL', b"&=" )
_add_tok('VBAREQUAL', b"|=" )
_add_tok('CIRCUMFLEXEQUAL', b"^=" )
_add_tok('LEFTSHIFTEQUAL', b"<<=" )
_add_tok('RIGHTSHIFTEQUAL', b">>=" )
_add_tok('DOUBLESTAREQUAL', b"**=" )
_add_tok('DOUBLESLASH', b"//" )
_add_tok('DOUBLESLASHEQUAL', b"//=" )
_add_tok('AT', b"@" )
_add_tok('OP')
_add_tok('ERRORTOKEN')

# extra PyPy-specific tokens
_add_tok("COMMENT")
_add_tok("NL")

# extra recovery-specific tokens
# those are never produced by the tokenizer, but the recovery algorithm can
# insert it
_add_tok("FAKESUITESTART") # behaves like: if 1: NEWLINE
_add_tok("FAKESUITE") # behaves like: INDENT pass DEDENT

del _add_tok

class _Tokens(object):
    pass
for name, idx in python_tokens.items():
    setattr(_Tokens, name, idx)
    tok_name[idx] = name
tokens = _Tokens()

del _Tokens, name
