# ______________________________________________________________________
"""Module automata

THIS FILE WAS COPIED FROM pypy/module/parser/pytokenize.py AND ADAPTED
TO BE ANNOTABLE (Mainly made the DFA's __init__ accept two lists
instead of a unique nested one)

$Id: automata.py,v 1.2 2003/10/02 17:37:17 jriehl Exp $
"""
# ______________________________________________________________________
# Module level definitions

# PYPY Modification: removed the EMPTY class as it's not needed here


# PYPY Modification: DEFAULT is a singleton, used only in the pre-RPython
# dicts (see pytokenize.py).  Then DFA.__init__() turns these dicts into
# more compact strings.

DEFAULT = object()

# PYPY Modification : removed all automata functions (any, maybe,
#                     newArcPair, etc.)

import six

ERROR_STATE_INT = 255
ERROR_STATE = six.int2byte(ERROR_STATE_INT)

class DFA:
    # ____________________________________________________________
    def __init__(self, states, accepts, start = 0):
        """ NOT_RPYTHON """
        assert len(states) < 255 # no support for huge amounts of states
        # construct string for looking up state transitions
        string_states = [] * len(states)
        # compute maximum
        maximum = 0
        for state in states:
            for key in state:
                assert isinstance(key, bytes) or key is DEFAULT
                if key == DEFAULT:
                    continue
                maximum = max(ord(key), maximum)
        self.max_char = maximum + 1

        defaults = []
        for i, state in enumerate(states):
            default = ERROR_STATE
            if DEFAULT in state:
                default = six.int2byte(state[DEFAULT])
            defaults.append(default)
            string_state = [default] * self.max_char
            for key, value in state.items():
                if key == DEFAULT:
                    continue
                assert len(key) == 1
                assert ord(key) < self.max_char
                string_state[ord(key)] = six.int2byte(value)
            string_states.extend(string_state)
        self.states = b"".join(string_states)
        self.defaults = b"".join(defaults)
        self.accepts = accepts
        self.start = start

    # ____________________________________________________________

    def _next_state(self, item, crntState):
        if item >= self.max_char:
            return six.indexbytes(self.defaults, crntState)
        else:
            return six.indexbytes(self.states, crntState * self.max_char + item)

    def recognize(self, inVec, pos = 0):
        crntState = self.start
        lastAccept = False
        i = pos
        for i in range(pos, len(inVec)):
            item = six.indexbytes(inVec, i)
            accept = self.accepts[crntState]
            crntState = self._next_state(item, crntState)
            if crntState != ERROR_STATE_INT:
                pass
            elif accept:
                return i
            elif lastAccept:
                # This is now needed b/c of exception cases where there are
                # transitions to dead states
                return i - 1
            else:
                return -1
            lastAccept = accept
        # if self.states[crntState][1]:
        if self.accepts[crntState]:
            return i + 1
        elif lastAccept:
            return i
        else:
            return -1

# ______________________________________________________________________

class NonGreedyDFA (DFA):

    def recognize(self, inVec, pos = 0):
        crntState = self.start
        i = pos
        for i in range(pos, len(inVec)):
            item = six.indexbytes(inVec, i)
            accept = self.accepts[crntState]
            if accept:
                return i
            crntState = self._next_state(item, crntState)
            if crntState == ERROR_STATE_INT:
                return -1
            i += 1
        if self.accepts[crntState]:
            return i
        else:
            return -1

# ______________________________________________________________________
# End of automata.py
