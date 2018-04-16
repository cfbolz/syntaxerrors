"""
A CPython inspired RPython parser.
"""


SHIFT = "SHIFT"
REDUCE = "REDUCE"
POP = "POP"
ERROR = "ERROR"

class Grammar(object):
    """
    Base Grammar object.

    Pass this to ParserGenerator.build_grammar to fill it with useful values for
    the Parser.
    """

    KEYWORD_TOKEN = -121212
    never_generate_as_fake = set()
    never_delete = set()

    def __init__(self):
        self.symbol_ids = {}
        self.symbol_names = {}
        self.symbol_to_label = {}
        self.keyword_ids = {}
        self.token_to_error_string = {}
        self.dfas = []
        self.labels = [0]
        self.token_ids = {}
        self.start = -1
        self._repair_fake_tokens = None

    def shared_copy(self):
        new = self.__class__()
        new.symbol_ids = self.symbol_ids
        new.symbols_names = self.symbol_names
        new.keyword_ids = self.keyword_ids
        new.dfas = self.dfas
        new.labels = self.labels
        new.token_ids = self.token_ids
        return new


    def classify(self, token):
        """Find the label for a token."""
        if token.token_type == self.KEYWORD_TOKEN:
            label_index = self.keyword_ids.get(token.value, -1)
            if label_index != -1:
                return label_index
        label_index = self.token_ids.get(token.token_type, -1)
        if label_index == -1:
            raise ParseError("invalid token", token)
        return label_index


    def repair_fake_tokens(self):
        if self._repair_fake_tokens:
            return self._repair_fake_tokens
        l = []
        for tp in self.token_ids:
            if tp in self.never_generate_as_fake:
                continue
            if tp == self.KEYWORD_TOKEN:
                keyword = "keyword"
                while keyword in self.keyword_ids:
                    keyword += "_"
                l.append((tp, keyword))
                for value in self.keyword_ids:
                    l.append((tp, value))
            else:
                l.append((tp, "fake"))
        self._repair_fake_tokens = l
        return l


class DFA(object):
    def __init__(self, grammar, symbol_id, states, first):
        self.grammar = grammar
        self.symbol_id = symbol_id
        self.states = states
        self.first = self._first_to_string(first)

    def could_match_token(self, label_index):
        pos = label_index >> 3
        bit = 1 << (label_index & 0b111)
        return bool(ord(self.first[label_index >> 3]) & bit)

    @staticmethod
    def _first_to_string(first):
        l = sorted(first.keys())
        b = bytearray(32)
        for label_index in l:
            pos = label_index >> 3
            bit = 1 << (label_index & 0b111)
            b[pos] |= bit
        return str(b)

    def __repr__(self):
        return "<DFA %s>" % (self.grammar.symbol_names[self.symbol_id], )


class Token(object):
    def __init__(self, token_type, value, lineno, column, line):
        self.token_type = token_type
        self.value = value
        self.lineno = lineno
        # 0-based offset
        self.column = column
        self.line = line

    def __repr__(self):
        return "Token(%s, %s)" % (self.token_type, self.value)

    def __eq__(self, other):
        # for tests
        return (
            self.token_type == other.token_type and
            self.value == other.value and
            self.lineno == other.lineno and
            self.column == other.column and
            self.line == other.line
        )

    def __ne__(self, other):
        return not self == other


class Node(object):

    __slots__ = ("type", "grammar")

    def __init__(self, grammar, type):
        self.grammar = grammar
        self.type = type

    def __eq__(self, other):
        raise NotImplementedError("abstract base class")

    def __ne__(self, other):
        return not self == other

    def get_value(self):
        return None

    def get_child(self, i):
        raise NotImplementedError("abstract base class")

    def num_children(self):
        return 0

    def append_child(self, child):
        raise NotImplementedError("abstract base class")

    def get_lineno(self):
        raise NotImplementedError("abstract base class")

    def get_column(self):
        raise NotImplementedError("abstract base class")

    def view(self):
        from dotviewer import graphclient
        import pytest
        r = ["digraph G {"]
        self._dot(r)
        r.append("}")
        p = pytest.ensuretemp("syntaxerrors").join("temp.dot")
        p.write("\n".join(r))
        graphclient.display_dot_file(str(p))

    def _dot(self, result):
        raise NotImplementedError("abstract base class")


class Terminal(Node):
    __slots__ = ("value", "lineno", "column")
    def __init__(self, grammar, token):
        Node.__init__(self, grammar, token.token_type)
        self.value = token.value
        self.lineno = token.lineno
        self.column = token.column

    def __repr__(self):
        return "Terminal(type=%s, value=%r)" % (self.type, self.value)

    def __eq__(self, other):
        # For tests.
        return (type(self) == type(other) and
                self.type == other.type and
                self.value == other.value)

    def get_value(self):
        return self.value

    def get_lineno(self):
        return self.lineno

    def get_column(self):
        return self.column

    def _dot(self, result):
        result.append('%s [label="%r", shape=box];' % (id(self), self.value))


class AbstractNonterminal(Node):
    __slots__ = ()

    def get_lineno(self):
        return self.get_child(0).get_lineno()

    def get_column(self):
        return self.get_child(0).get_column()

    def __eq__(self, other):
        # For tests.
        # grumble, annoying
        if not isinstance(other, AbstractNonterminal):
            return False
        if self.type != other.type:
            return False
        if self.num_children() != other.num_children():
            return False
        for i in range(self.num_children()):
            if self.get_child(i) != other.get_child(i):
                return False
        return True

    def _dot(self, result):
        for i in range(self.num_children()):
            child = self.get_child(i)
            result.append('%s [label=%s, shape=box]' % (id(self), self.grammar.symbol_names[self.type]))
            result.append('%s -> %s [label="%s"]' % (id(self), id(child), i))
            child._dot(result)

class Nonterminal(AbstractNonterminal):
    __slots__ = ("_children", )
    def __init__(self, grammar, type, children=None):
        Node.__init__(self, grammar, type)
        if children is None:
            children = []
        self._children = children

    def __repr__(self):
        return "Nonterminal(type=%s, children=%r)" % (self.type, self._children)

    def get_child(self, i):
        assert self._children is not None
        return self._children[i]

    def num_children(self):
        return len(self._children)

    def append_child(self, child):
        return Nonterminal(self.grammar, self.type, self._children + [child])


class Nonterminal1(AbstractNonterminal):
    __slots__ = ("_child", )
    def __init__(self, grammar, type, child):
        Node.__init__(self, grammar, type)
        self._child = child

    def __repr__(self):
        return "Nonterminal(type=%s, children=[%r])" % (self.type, self._child)

    def get_child(self, i):
        assert i == 0 or i == -1
        return self._child

    def num_children(self):
        return 1

    def append_child(self, child):
        assert 0, "should be unreachable"


class ParseError(Exception):
    pass

class SingleParseError(ParseError):
    def __init__(self, msg, token, expected=-1, expected_str=None):
        self.msg = msg
        self.token = token
        self.expected = expected
        self.expected_str = expected_str

    def __str__(self):
        return "ParserError(%s)" % (self.token, )

class MultipleParseError(ParseError):
    def __init__(self, errors):
        self.errors = errors


class Done(Exception):
    def __init__(self, node):
        self.node = node


class StackEntry(object):
    def __init__(self, next, dfa, state, node=None):
        self.next = next
        self.dfa = dfa
        self.state = state
        self.node = node

    def push(self, dfa, state):
        return StackEntry(self, dfa, state)

    def pop(self):
        return self.next

    def node_append_child(self, child):
        node = self.node
        if node is None:
            newnode = Nonterminal1(self.dfa.grammar, self.dfa.symbol_id, child)
        elif isinstance(node, Nonterminal1):
            newnode = Nonterminal(
                    self.dfa.grammar, self.dfa.symbol_id, [node._child, child])
        else:
            newnode = self.node.append_child(child)
        return StackEntry(self.next, self.dfa, self.state, newnode)

    def switch_state(self, state):
        return StackEntry(self.next, self.dfa, state, self.node)

    def reduce(self, next_dfa, next_state):
        """Push a terminal and adjust the current state."""
        self = self.switch_state(next_state)
        return self.push(next_dfa, 0)

    def pop_node(self):
        """Pop an entry off the stack and make its node a child of the last."""
        node = self.node
        self = self.pop()
        if self:
            return self.node_append_child(node)
        else:
            raise Done(node)

    def shift(self, grammar, next_state, token):
        """shift a non-terminal and prepare for the next state."""
        new_node = Terminal(grammar, token)
        self = self.node_append_child(new_node)
        return self.switch_state(next_state)

    def shift_pop(self, grammar, next_state, token):
        stack = self.shift(grammar, next_state, token)
        state = self.dfa.states[next_state]
        # While the only possible action is to accept, pop nodes off
        # the stack.
        while state[1] and not state[0]:
            stack = stack.pop_node()
            assert stack is not None
            dfa = stack.dfa
            state_index = stack.state
            state = dfa.states[state_index]
        return stack

    def view(self):
        from dotviewer import graphclient
        import pytest
        r = ["digraph G {"]
        self._dot(r)
        r.append("}")
        p = pytest.ensuretemp("syntaxerrors").join("temp.dot")
        p.write("\n".join(r))
        graphclient.display_dot_file(str(p))

    def _dot(self, result):
        result.append('%s [label=%s, shape=box, color=white]' % (id(self), self.dfa.grammar.symbol_names[self.dfa.symbol_id]))
        if self.next:
            result.append('%s -> %s [label="next"]' % (id(self), id(self.next)))
            self.next._dot(result)
        if self.node:
            result.append('%s -> %s [label="node"]' % (id(self), id(self.node)))
            self.node._dot(result)


class Parser(object):

    def __init__(self, grammar):
        self.grammar = grammar
        self.root = None

    def prepare(self, start=-1):
        """Setup the parser for parsing.

        Takes the starting symbol as an argument.
        """
        if start == -1:
            start = self.grammar.start
        self.root = None
        self.start = start

    def add_tokens(self, tokens):
        from syntaxerrors.recovery import try_recover
        grammar = self.grammar
        stack = StackEntry(None, grammar.dfas[self.start - 256], 0)
        errors = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            label_index = grammar.classify(token)
            try:
                stack = add_token(stack, grammar, token, label_index)
            except ParseError as e:
                errors.append(e)
                tokens, i, stack = try_recover(grammar, stack, tokens, i)
                if i == -1:
                    break
            except Done as e:
                self.root = e.node
                break
            else:
                i += 1
        if errors:
            self.root = None
            if len(errors) == 1:
                raise errors[0]
            else:
                raise MultipleParseError(errors)


def add_token(stack, grammar, token, label_index):
    orig_stack = stack
    while True:
        action, next_state, sub_node_dfa = find_action(stack, grammar, token, label_index)
        dfa = stack.dfa
        state_index = stack.state
        states = dfa.states
        if action == SHIFT:
            # We matched a non-terminal.
            return stack.shift_pop(grammar, next_state, token)
        elif action == REDUCE:
            stack = stack.reduce(sub_node_dfa, next_state)
        elif action == POP:
            try:
                stack = stack.pop_node()
            except Done as e:
                XXX #?
            if stack is None:
                raise SingleParseError("too much input", token)
        else:
            assert action == ERROR
            arcs, is_accepting = states[state_index]
            # We failed to find any arcs to another state, so unless this
            # state is accepting, it's invalid input.
            # If only one possible input would satisfy, attach it to the
            # error.
            if len(arcs) == 1:
                expected = grammar.labels[arcs[0][0]]
                expected_str = grammar.token_to_error_string.get(
                        arcs[0][0], None)
            else:
                expected = -1
                expected_str = None

            raise SingleParseError("bad input", token, expected, expected_str)

def find_action(stack, grammar, token, label_index):
    dfa = stack.dfa
    state_index = stack.state
    states = dfa.states
    arcs, is_accepting = states[state_index]
    for i, next_state in arcs:
        sym_id = grammar.labels[i]
        if label_index == i:
            # We matched a non-terminal.
            return SHIFT, next_state, None
        elif sym_id >= 256:
            sub_node_dfa = grammar.dfas[sym_id - 256]
            # Check if this token can start a child node.
            if sub_node_dfa.could_match_token(label_index):
                return REDUCE, next_state, sub_node_dfa
    else:
        if is_accepting:
            return POP, None, None
        return ERROR, None, None
