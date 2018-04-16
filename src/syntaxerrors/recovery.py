from collections import deque

from syntaxerrors import parser

# number of tokens that must be successfully parsed after the next newline for
# the repair to be considered a success
SUCCESS_NUMBER_TOKENS = 5

# number of existing tokens allowed in a repair
NUMBER_EXISTING = 6

# number of inserts allowed in a repair
NUMBER_INSERTS = 4

# number of deletes allowed in a repair
NUMBER_DELETES = 3

# number of repair attempts to try
ATTEMPTS_LIMIT = 100000

class Repair(object):
    def __init__(self, stack, tokens, index, name='', reprtokens=None):
        self.stack = stack
        self.tokens = tokens
        self.index = index
        self.name = name
        if reprtokens is None:
            reprtokens = []
        self.reprtokens = reprtokens

    def __repr__(self):
        l = []
        for i, c in enumerate(self.name):
            l.append({'e': 'existing', 'd': 'delete', 'i': 'insert'}[c])
            l.append(self.reprtokens[i])
        return "<Repair %s %s>" % (self.name, l)

    def parses_successfully(self, grammar, endindex):
        stack = self.stack
        for i in range(self.index, endindex):
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
        token = self.tokens[self.index]
        # consume existing token
        if self.name and self.name.count("e") < NUMBER_EXISTING:
            label_index = grammar.classify(token)
            try:
                stack = parser.add_token(self.stack, grammar, token, label_index)
            except parser.ParseError:
                pass
            else:
                yield Repair(stack, self.tokens, self.index + 1, self.name + 'e', self.reprtokens + [token])

        # delete next token
        if (self.name.count("d") < NUMBER_DELETES and (self.name == '' or self.name[-1] != 'i') and
                self.tokens[self.index].token_type not in grammar.never_delete):
            yield Repair(self.stack, self.tokens, self.index + 1, self.name + 'd', self.reprtokens + [token])

        # insert token
        if self.name.count("i") < NUMBER_INSERTS:
            for tp, value in grammar.repair_fake_tokens():
                token = parser.Token(tp, value, -1, -1, "fake line")
                label_index = grammar.classify(token)
                try:
                    stack = parser.add_token(self.stack, grammar, token, label_index)
                except parser.ParseError:
                    continue
                yield Repair(stack, self.tokens, self.index, self.name + 'i', self.reprtokens + [token])


def initial_queue(stack, tokens, index):
    return [Repair(stack, tokens, index)]

def try_recover(grammar, stack, tokens, index):
    queue = initial_queue(stack, tokens, index)
    endindex = compute_endindex(tokens, index)
    attempts = 0
    while queue:
        newqueue = []
        for element in queue:
            for repair in element.further_changes(grammar):
                attempts += 1
                if attempts > ATTEMPTS_LIMIT:
                    break
                if attempts % 10000 == 0:
                    print attempts, len(newqueue)
                if repair.parses_successfully(grammar, endindex):
                    assert repair.name
                    print '=====', repair.name, repair
                    return repair.tokens, repair.index, repair.stack
                newqueue.append(repair)
        queue = newqueue
    assert 0, "no recovery found! despite trying %s" % (attempts, )

def compute_endindex(tokens, index):
    endindex = index
    lineno = tokens[index].lineno
    for endindex in range(index, len(tokens)):
        token = tokens[endindex]
        if token.lineno > lineno:
            break
    endindex += SUCCESS_NUMBER_TOKENS
    return min(len(tokens), endindex)
