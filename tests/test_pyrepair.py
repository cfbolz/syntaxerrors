from __future__ import print_function
import os

import pytest

from syntaxerrors import pyparse
from syntaxerrors.error import MultipleSyntaxErrors

def test_find_four_errors():
    info = pyparse.CompileInfo("<string>", "exec")
    p = pyparse.PythonParser()
    try:
        st = p.parse_source(b"""
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
        st = p.parse_source(b"""
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
        st = p.parse_source(b"""
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
        print(pyparse.format_messages(e))

def test_lambda_with_newlines():
    info = pyparse.CompileInfo("<string>", "exec")
    p = pyparse.PythonParser()
    try:
        st = p.parse_source(b"""
lambda x:
    x + 1

print 2

if a
    print 2

""", info)
    except MultipleSyntaxErrors as e:
        assert len(e.errors) == 2
        assert [x.lineno for x in e.errors] == [2, 7]
        print(pyparse.format_messages(e))


def test_missing_comma_list():
    info = pyparse.CompileInfo("<string>", "exec")
    p = pyparse.PythonParser()
    try:
        st = p.parse_source(b"""
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
        print(pyparse.format_messages(e))

def test_genexp_keywordarg():
    info = pyparse.CompileInfo("<string>", "exec")
    p = pyparse.PythonParser()
    try:
        st = p.parse_source(b"""
dict(a = i for i in range(10))
print 1
if a
    print 3
""", info)
    except MultipleSyntaxErrors as e:
        assert len(e.errors) == 2
        assert [x.lineno for x in e.errors] == [2, 4]
        print(pyparse.format_messages(e))


def test_genexp_tuple():
    info = pyparse.CompileInfo("<string>", "exec")
    p = pyparse.PythonParser()
    try:
        st = p.parse_source(b"""
(a, b for a, b in zip([1, 2], [3, 4]))
print 1
if a
    print 3
""", info)
    except MultipleSyntaxErrors as e:
        assert len(e.errors) == 2
        assert [x.lineno for x in e.errors] == [2, 4]
        print(pyparse.format_messages(e))


def test_missing_newline():
    info = pyparse.CompileInfo("<string>", "exec")
    p = pyparse.PythonParser()
    try:
        st = p.parse_source(b"""
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
        print(pyparse.format_messages(e))

def test_extra_dot():
    info = pyparse.CompileInfo("<string>", "exec")
    p = pyparse.PythonParser()
    try:
        st = p.parse_source(b"""
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
        print(pyparse.format_messages(e))

def Xtest_indent_broken():

    info = pyparse.CompileInfo("<string>", "exec")
    p = pyparse.PythonParser()
    try:
        st = p.parse_source(b"""
try:
    stack = add_token(stack, grammar, token, label_index)
except ParseError as e:
    errors.append(e)
    tokens, i, stack = try_recover(grammar, stack, tokens, i)
    if i == -1:
        break
except Done as e:
%   self.root = e.node
    break

print 17

if x
    print 3
""", info)
    except MultipleSyntaxErrors as e:
        assert len(e.errors) == 2
        assert [x.lineno for x in e.errors] == [5, 10]
        print(pyparse.format_messages(e))



def Xtest_random_newline():
    info = pyparse.CompileInfo("<string>", "exec")
    p = pyparse.PythonParser()
    try:
        st = p.parse_source(b"""
try:
    1/0
exc
  ept ZeroDivisionError as e:
    foo.bar.baz
else:
    blub

print 17

if x
    print 3
""", info)
    except MultipleSyntaxErrors as e:
        assert len(e.errors) == 2
        assert [x.lineno for x in e.errors] == [5, 10]
        print(pyparse.format_messages(e))

def test_random_comment():
    info = pyparse.CompileInfo("<string>", "exec")
    p = pyparse.PythonParser()
    try:
        st = p.parse_source(b"""
def add_tokens(self, tokens):
    from #yntaxerrors.recovery import try_recover
    grammar = self.grammar
    stack = StackEntry(None, grammar.dfas[self.start - 256], 0)

print 17

if x
    print 3
""", info)
    except MultipleSyntaxErrors as e:
        assert len(e.errors) == 2
        assert [x.lineno for x in e.errors] == [3, 9]
        print(pyparse.format_messages(e))

def test_need_to_fix_earlier():
    import six
    if six.PY3:
        pytest.skip("later")
    info = pyparse.CompileInfo("<string>", "exec")
    p = pyparse.PythonParser()
    try:
        st = p.parse_source(b"""
de% blub(self, tokens):
    grammar = self.grammar
    stack = StackEntry(None, grammar.dfas[self.start - 256], 0)

print 17

if x
    print 3
""", info)
    except MultipleSyntaxErrors as e:
        assert len(e.errors) == 2
        assert [x.lineno for x in e.errors] == [2, 8]
        print(pyparse.format_messages(e))
