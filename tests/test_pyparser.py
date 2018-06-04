import os

import pytest

from syntaxerrors import pyparse
from syntaxerrors.parser import MultipleParseError

srcdir = os.path.dirname(pyparse.__file__)

def test_simple():
    info = pyparse.CompileInfo("<string>", "exec")
    p = pyparse.PythonParser()
    st = p.parse_source(b"x = 1\n", info)

def test_parse_all():
    # smoke test
    for fn in os.listdir(srcdir):
        if fn.endswith(".py"):
            fn = os.path.join(srcdir, fn)
            with open(fn, "rb") as f:
                s = f.read()
            info = pyparse.CompileInfo(fn, "exec")
            p = pyparse.PythonParser()
            st = p.parse_source(s, info)

