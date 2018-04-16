import os

import pytest

from syntaxerrors import pyparse
from syntaxerrors.error import MultipleSyntaxErrors

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
    except MultipleSyntaxErrors as e:
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
    except MultipleSyntaxErrors as e:
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

print 2 + 2

if a
    print 2

""", info)
    except MultipleSyntaxErrors as e:
        assert len(e.errors) == 2
        assert [x.lineno for x in e.errors] == [4, 9]
        print pyparse.format_messages(e)

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
    except MultipleSyntaxErrors as e:
        assert len(e.errors) == 2
        assert [x.lineno for x in e.errors] == [2, 7]
        print pyparse.format_messages(e)


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
    except MultipleSyntaxErrors as e:
        assert len(e.errors) == 2
        assert [x.lineno for x in e.errors] == [4, 14]
        print pyparse.format_messages(e)

def test_genexp_keywordarg():
    info = pyparse.CompileInfo("<string>", "exec")
    p = pyparse.PythonParser()
    try:
        st = p.parse_source("""
dict(a = i for i in range(10))
print 1
if a
    print 3
""", info)
    except MultipleSyntaxErrors as e:
        assert len(e.errors) == 2
        assert [x.lineno for x in e.errors] == [2, 4]
        print pyparse.format_messages(e)


def test_genexp_tuple():
    info = pyparse.CompileInfo("<string>", "exec")
    p = pyparse.PythonParser()
    try:
        st = p.parse_source("""
(a, b for a, b in zip([1, 2], [3, 4]))
print 1
if a
    print 3
""", info)
    except MultipleSyntaxErrors as e:
        assert len(e.errors) == 2
        assert [x.lineno for x in e.errors] == [2, 4]
        print pyparse.format_messages(e)


def test_missing_newline():
    info = pyparse.CompileInfo("<string>", "exec")
    p = pyparse.PythonParser()
    try:
        st = p.parse_source("""
if 1: def some_complicated_function(w, ith, many, tokens):
        if a:
            print 2
        else:
            print 3

if x
    print 3
""", info)
    except MultipleSyntaxErrors as e:
        assert len(e.errors) == 2
        assert [x.lineno for x in e.errors] == [2, 8]
        print pyparse.format_messages(e)

def test_extra_dot():
    info = pyparse.CompileInfo("<string>", "exec")
    p = pyparse.PythonParser()
    try:
        st = p.parse_source("""
if 1:
    if errors:
        self.root = None
        if len(error.) == 1:
            raise errors[0]
        else:
            raise MultipleParseError(errors)

if x
    print 3
""", info)
    except MultipleSyntaxErrors as e:
        assert len(e.errors) == 2
        assert [x.lineno for x in e.errors] == [5, 10]
        print pyparse.format_messages(e)
