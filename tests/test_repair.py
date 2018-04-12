import pytest

from syntaxerrors import parser, recovery

def test_generate_fake_tokens():
    gram = parser.Grammar()
    gram.token_ids[1] = 2
    gram.token_ids[3] = 5
    assert gram.repair_fake_tokens() == [(1, "fake"), (3, "fake")]

def test_blacklist_token():
    gram = parser.Grammar()
    gram.token_ids[1] = 2
    gram.token_ids[3] = 5
    gram.never_generate_as_fake = {3}
    assert gram.repair_fake_tokens() == [(1, "fake")]
