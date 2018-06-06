# New parser tests.
import pytest
import tokenize
import token
from syntaxerrors import parser, metaparser, pygram, pytokenizer

from tests.test_metaparser import MyGrammar


def test_char_set():
    first = {5: None, 9: None, 100: None, 255:None}
    p = parser.DFA(None, None, None, first)
    for i in range(256):
        assert p.could_match_token(i) == (i in first)

class SimpleParser(parser.Parser):

    def parse(self, input):
        self.prepare()
        tokens = pytokenizer.generate_tokens(input.splitlines(True), 0)
        self.add_tokens(tokens)
        return self.root


def tree_from_string(expected, gram):
    def count_indent(s):
        indent = 0
        for char in s:
            if char != " ":
                break
            indent += 1
        return indent
    last_newline_index = 0
    for i, char in enumerate(expected):
        if char == "\n":
            last_newline_index = i
        elif char != " ":
            break
    if last_newline_index:
        expected = expected[last_newline_index + 1:]
    base_indent = count_indent(expected)
    assert not divmod(base_indent, 4)[1], "not using 4 space indentation"
    lines = [line[base_indent:] for line in expected.splitlines()]
    last_indent = 0
    node_stack = []
    for line in lines:
        if not line.strip():
            continue
        data = line.split()
        if data[0].isupper():
            tp = getattr(token, data[0])
            if len(data) == 2:
                value = data[1].strip(u"\"")
            elif tp == token.NEWLINE:
                value = u"\n"
            else:
                value = u""
            n = parser.Terminal(gram, tp, value, 0, 0)
        else:
            tp = gram.symbol_ids[data[0]]
            n = parser.Nonterminal(gram, tp)
        new_indent = count_indent(line)
        if new_indent >= last_indent:
            if new_indent == last_indent and node_stack:
                node_stack.pop()
            if node_stack:
                node_stack[-1]._children.append(n)
            node_stack.append(n)
        else:
            diff = last_indent - new_indent
            pop_nodes = diff // 4 + 1
            del node_stack[-pop_nodes:]
            node_stack[-1]._children.append(n)
            node_stack.append(n)
        last_indent = new_indent
    return node_stack[0]


class TestParser:

    def parser_for(self, gram, add_endmarker=True):
        assert isinstance(gram, bytes)
        if add_endmarker:
            gram += b" NEWLINE+ ENDMARKER\n"
        pgen = metaparser.ParserGenerator(gram)
        g = pgen.build_grammar(MyGrammar)
        return SimpleParser(g), g

    def test_multiple_rules(self):
        gram = b"""foo: 'next_rule' bar 'end' NEWLINE+ ENDMARKER
bar: NAME NUMBER\n"""
        p, gram = self.parser_for(gram, False)
        expected = u"""
        foo
            NAME "next_rule"
            bar
                NAME "a_name"
                NUMBER "42"
            NAME "end"
            NEWLINE
            NEWLINE
            ENDMARKER"""
        input = b"next_rule a_name 42 end"
        assert tree_from_string(expected, gram) == p.parse(input)

    def test_recursive_rule(self):
        gram = b"""foo: NAME bar STRING NEWLINE+ ENDMARKER
bar: NAME [bar] NUMBER\n"""
        p, gram = self.parser_for(gram, False)
        expected = u"""
        foo
            NAME "hi"
            bar
                NAME "hello"
                bar
                    NAME "a_name"
                    NUMBER "32"
                NUMBER "42"
            STRING "'string'"
            NEWLINE
            NEWLINE
            ENDMARKER"""
        input = b"hi hello a_name 32 42 'string'"
        assert tree_from_string(expected, gram) == p.parse(input)

    def test_symbol(self):
        gram = b"""parent: first_child second_child NEWLINE+ ENDMARKER
first_child: NAME age
second_child: STRING
age: NUMBER\n"""
        p, gram = self.parser_for(gram, False)
        expected = u"""
        parent
            first_child
                NAME "harry"
                age
                     NUMBER "13"
            second_child
                STRING "'fred'"
            NEWLINE
            NEWLINE
            ENDMARKER"""
        input = b"harry 13 'fred'"
        assert tree_from_string(expected, gram) == p.parse(input)

    def test_token(self):
        p, gram = self.parser_for(b"foo: NAME")
        expected = u"""
        foo
           NAME "hi"
           NEWLINE
           NEWLINE
           ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse(b"hi")
        pytest.raises(parser.ParseError, p.parse, b"567")
        p, gram = self.parser_for(b"foo: NUMBER NAME STRING")
        expected = u"""
        foo
            NUMBER "42"
            NAME "hi"
            STRING "'bar'"
            NEWLINE
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse(b"42 hi 'bar'")

    def test_optional(self):
        p, gram = self.parser_for(b"foo: [NAME] 'end'")
        expected = u"""
        foo
            NAME "hi"
            NAME "end"
            NEWLINE
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse(b"hi end")
        expected = u"""
        foo
            NAME "end"
            NEWLINE
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse(b"end")

    def test_grouping(self):
        p, gram = self.parser_for(
            b"foo: ((NUMBER NAME | STRING) | 'second_option')")
        expected = u"""
        foo
            NUMBER "42"
            NAME "hi"
            NEWLINE
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse(b"42 hi")
        expected = u"""
        foo
            STRING "'hi'"
            NEWLINE
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse(b"'hi'")
        expected = u"""
        foo
            NAME "second_option"
            NEWLINE
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse(b"second_option")
        pytest.raises(parser.ParseError, p.parse, b"42 a_name 'hi'")
        pytest.raises(parser.ParseError, p.parse, b"42 second_option")

    def test_alternative(self):
        p, gram = self.parser_for(b"foo: (NAME | NUMBER)")
        expected = u"""
        foo
            NAME "hi"
            NEWLINE
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse(b"hi")
        expected = u"""
        foo
            NUMBER "42"
            NEWLINE
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse(b"42")
        pytest.raises(parser.ParseError, p.parse, b"hi 23")
        pytest.raises(parser.ParseError, p.parse, b"23 hi")
        pytest.raises(parser.ParseError, p.parse, b"'some string'")

    def test_keyword(self):
        p, gram = self.parser_for(b"foo: 'key'")
        expected = u"""
        foo
            NAME "key"
            NEWLINE
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse(b"key")
        pytest.raises(parser.ParseError, p.parse, b"")
        p, gram = self.parser_for(b"foo: NAME 'key'")
        expected = u"""
        foo
            NAME "some_name"
            NAME "key"
            NEWLINE
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse(b"some_name key")
        pytest.raises(parser.ParseError, p.parse, b"some_name")

    def test_repeaters(self):
        p, gram = self.parser_for(b"foo: NAME+ 'end'")
        expected = u"""
        foo
            NAME "hi"
            NAME "bye"
            NAME "nothing"
            NAME "end"
            NEWLINE
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse(b"hi bye nothing end")
        pytest.raises(parser.ParseError, p.parse, b"end")
        pytest.raises(parser.ParseError, p.parse, b"hi bye")
        p, gram = self.parser_for(b"foo: NAME* 'end'")
        expected = u"""
        foo
            NAME "hi"
            NAME "bye"
            NAME "end"
            NEWLINE
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse(b"hi bye end")
        pytest.raises(parser.ParseError, p.parse, b"hi bye")
        expected = u"""
        foo
            NAME "end"
            NEWLINE
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse(b"end")

        p, gram = self.parser_for(b"foo: (NAME | NUMBER)+ 'end'")
        expected = u"""
        foo
            NAME "a_name"
            NAME "name_two"
            NAME "end"
            NEWLINE
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse(b"a_name name_two end")
        expected = u"""
        foo
            NUMBER "42"
            NAME "name"
            NAME "end"
            NEWLINE
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse(b"42 name end")
        pytest.raises(parser.ParseError, p.parse, b"end")
        p, gram = self.parser_for(b"foo: (NAME | NUMBER)* 'end'")
        expected = u"""
        foo
            NAME "hi"
            NUMBER 42
            NAME "end"
            NEWLINE
            NEWLINE
            ENDMARKER"""
        assert tree_from_string(expected, gram) == p.parse(b"hi 42 end")


    def test_optimized_terminal(self):
        gram = b"""foo: bar baz 'end' NEWLINE+ ENDMARKER
bar: NAME
baz: NUMBER
"""
        p, gram = self.parser_for(gram, False)
        expected = u"""
        foo
            bar
                NAME "a_name"
            baz
                NUMBER "42"
            NAME "end"
            NEWLINE
            NEWLINE
            ENDMARKER"""
        input = b"a_name 42 end"
        tree = p.parse(input)
        assert tree_from_string(expected, gram) == tree
        assert isinstance(tree, parser.Nonterminal)
        assert isinstance(tree.get_child(0), parser.Nonterminal1)
        assert isinstance(tree.get_child(1), parser.Nonterminal1)


    def test_error_string(self):
        p, gram = self.parser_for(
            b"foo: 'if' NUMBER '+' NUMBER"
        )
        info = pytest.raises(parser.ParseError, p.parse, b"if 42")
        info.value.expected_str is None
        info = pytest.raises(parser.ParseError, p.parse, b"if 42 42")
        info.value.expected_str == '+'

