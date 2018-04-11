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
    def __init__(self, stack, tokens, index, name='', nshifts=0, ninserts=0, ndeletes=0):
        self.stack = stack
        self.tokens = tokens
        self.index = index
        self.name = name
        self.nshifts = nshifts
        self.ninserts = ninserts
        self.ndeletes = ndeletes

    def parses_successfully(self, grammar):
        stack = self.stack
        for i in range(self.index, min(len(self.tokens), self.index + SUCCESS_NUMBER_TOKENS)):
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
        if self.nshifts < NUMBER_SHIFTS:
            token = self.tokens[self.index]
            label_index = grammar.classify(token)
            token_type, value, lineno, column, line = token
            action, next_state, _ = parser.find_action(self.stack, grammar, token, label_index)
            if action == parser.SHIFT:
                stack = self.stack.shift_pop(grammar, next_state, token_type, value, lineno, column)
                yield Repair(stack, self.tokens, self.index + 1, self.name + 's', self.nshifts + 1, self.ninserts, self.ndeletes)

        # delete next token
        if self.ndeletes < NUMBER_DELETES and (self.name == '' or self.name[-1] != 'i'):
            yield Repair(self.stack, self.tokens, self.index + 1, self.name + 'd', self.nshifts, self.ninserts, self.ndeletes + 1)

        # insert token
        if self.ndeletes < NUMBER_INSERTS:
            for tp, value in find_fake_tp_value_pairs(grammar):
                token = tp, value, -1, -1, "fake line"
                label_index = grammar.classify(token)
                try:
                    stack = parser.add_token(self.stack, grammar, token, label_index)
                except parser.ParseError:
                    continue
                yield Repair(stack, self.tokens, self.index, self.name + 'i', self.nshifts, self.ninserts + 1, self.ndeletes)

def find_fake_tp_value_pairs(grammar):
    for tp in grammar.token_ids:
        if tp == grammar.KEYWORD_TOKEN:
            for value in grammar.keyword_ids:
                yield tp, value
        else:
            yield tp, "fake"

def initial_queue(stack, tokens, index):
    return [Repair(stack, tokens, index)]

def try_recover(grammar, stack, tokens, index):
    import pdb; pdb.set_trace()
    queue = initial_queue(stack, tokens, index)
    while queue:
        newqueue = []
        for element in queue:
            for repair in element.further_changes(grammar):
                if repair.parses_successfully(grammar):
                    assert not (repair.ninserts == repair.ndeletes == repair.nshifts == 0)
                    print '=====', repair.name
                    return repair.tokens, repair.index, repair.stack
                newqueue.append(repair)
        queue = newqueue
