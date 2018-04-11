import os

import pytest

from syntaxerrors import pyparse
from syntaxerrors.parser import MultipleParseError

srcdir = os.path.dirname(pyparse.__file__)

def test_simple():
    info = pyparse.CompileInfo("<string>", "exec")
    p = pyparse.PythonParser()
    st = p.parse_source("x = 1\n", info)

def test_parse_all():
    # smoke test
    for fn in os.listdir(srcdir):
        if fn.endswith(".py"):
            fn = os.path.join(srcdir, fn)
            with open(fn) as f:
                s = f.read()
            info = pyparse.CompileInfo(fn, "exec")
            p = pyparse.PythonParser()
            st = p.parse_source(s, info)

def test_find_four_errors():
    info = pyparse.CompileInfo("<string>", "exec")
    p = pyparse.PythonParser()
    try:
        st = p.parse_source("""
if a
    print 2

x +=

print 4

x * * * * x

for i in range(10):
    print i

i += 1

if a
    print 5

""", info)
    except MultipleParseError as e:
        assert len(e.errors) == 4
        assert [x.lineno for x in e.errors] == [2, 5, 9, 16]
        msg = pyparse.format_messages(e)
        assert msg == """\
if a
    ^
invalid syntax (expected ':') (line 2)


___
There were possibly further errors, but they are guesses:
(This is an experimental feature! if the errors are nonsense, please report a bug!)

x +=
    ^
invalid syntax (line 5)

x * * * * x
    ^
invalid syntax (line 9)

if a
    ^
invalid syntax (expected ':') (line 16)
"""
    else:
        assert 0, "should have raised"



def test_further_examples():
    info = pyparse.CompileInfo("<string>", "exec")
    p = pyparse.PythonParser()
    try:
        st = p.parse_source("""
def f(a, e.expected):
    bla

a.b(1, 2, 3):

def f(self):

print b

""", info)
    except MultipleParseError as e:
        assert len(e.errors) == 3
        assert [x.lineno for x in e.errors] == [2, 5, 9]
        msg = pyparse.format_messages(e)
        assert msg == """\
def f(a, e.expected):
          ^
invalid syntax (expected ')') (line 2)


___
There were possibly further errors, but they are guesses:
(This is an experimental feature! if the errors are nonsense, please report a bug!)

a.b(1, 2, 3):
            ^
invalid syntax (line 5)

print b
^
expected an indented block (line 9)
"""
    else:
        assert 0, "should have raised"


def test_missing_pass():
    info = pyparse.CompileInfo("<string>", "exec")
    p = pyparse.PythonParser()
    try:
        st = p.parse_source("""
if x:
    # nothing
else:
    print 2

if a
    print 2

""", info)
    except MultipleParseError as e:
        assert len(e.errors) == 2
        assert [x.lineno for x in e.errors] == [4, 7]

@pytest.mark.xfail
def test_lambda_with_newlines():
    info = pyparse.CompileInfo("<string>", "exec")
    p = pyparse.PythonParser()
    try:
        st = p.parse_source("""
lambda x:
    x + 1

print 2

if a
    print 2

""", info)
    except MultipleParseError as e:
        assert len(e.errors) == 2
        assert [x.lineno for x in e.errors] == [4, 7]


def test_missing_comma_list():
    info = pyparse.CompileInfo("<string>", "exec")
    p = pyparse.PythonParser()
    try:
        st = p.parse_source("""
[1,
2
3,
5,
5,
3,
4,
5,
1,
2,
]

if a
    print 2

""", info)
    except MultipleParseError as e:
        assert len(e.errors) == 2
        assert [x.lineno for x in e.errors] == [4, 14]
