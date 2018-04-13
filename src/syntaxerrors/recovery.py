from collections import deque

from syntaxerrors import parser

# number of tokens that must be successfully parsed for the algorithm to be
# considered a success
SUCCESS_NUMBER_TOKENS = 5

# number of shifts allowed in a repair
NUMBER_SHIFTS = 4

# number of inserts allowed in a repair
NUMBER_INSERTS = 4

# number of deletes allowed in a repair
NUMBER_DELETES = 3

class Repair(object):
    def __init__(self, stack, tokens, index, name='', tokrepr=None):
        self.stack = stack
        self.tokens = tokens
        self.index = index
        self.name = name
        if tokrepr is None:
            tokrepr = []
        self.tokrepr = tokrepr

    def __repr__(self):
        return "<Repair %s %s>" % (self.name, self.tokrepr)

    def parses_successfully(self, grammar):
        stack = self.stack
        endindex = self.index + SUCCESS_NUMBER_TOKENS# + self.name.count("i")
        for i in range(self.index, min(len(self.tokens), endindex)):
            token = self.tokens[i]
            label_index = grammar.classify(token)
            try:
                stack = parser.add_token(stack, grammar, token, label_index)
            except parser.ParseError:
                return False
            except parser.Done:
                return True
        return True

    def further_changes(self, grammar):
        # shift
        if self.name.count("s") < NUMBER_SHIFTS:
            token = self.tokens[self.index]
            label_index = grammar.classify(token)
            token_type, value, lineno, column, line = token
            action, next_state, _ = parser.find_action(self.stack, grammar, token, label_index)
            if action == parser.SHIFT:
                stack = self.stack.shift_pop(grammar, next_state, token_type, value, lineno, column)
                yield Repair(stack, self.tokens, self.index + 1, self.name + 's', self.tokrepr)

        # delete next token
        if self.name.count("d") < NUMBER_DELETES and (self.name == '' or self.name[-1] != 'i'):
            tokname, = [name for name, x in grammar.TOKENS.items() if x == self.tokens[self.index][0]]
            yield Repair(self.stack, self.tokens, self.index + 1, self.name + 'd', self.tokrepr + ["delete " + tokname])

        # insert token
        if self.name.count("i") < NUMBER_INSERTS:
            for tp, value in grammar.repair_fake_tokens():
                token = tp, value, -1, -1, "fake line"
                label_index = grammar.classify(token)
                try:
                    stack = parser.add_token(self.stack, grammar, token, label_index)
                except parser.ParseError:
                    continue
                tokname, = [name for name, x in grammar.TOKENS.items() if x == tp]
                yield Repair(stack, self.tokens, self.index, self.name + 'i', self.tokrepr + ["insert " + tokname])


def initial_queue(stack, tokens, index):
    return [Repair(stack, tokens, index)]

def try_recover(grammar, stack, tokens, index):
    queue = initial_queue(stack, tokens, index)
    while queue:
        newqueue = []
        for element in queue:
            for repair in element.further_changes(grammar):
                if repair.parses_successfully(grammar):
                    assert repair.name
                    print '=====', repair.name, repair
                    return repair.tokens, repair.index, repair.stack
                newqueue.append(repair)
        queue = newqueue
