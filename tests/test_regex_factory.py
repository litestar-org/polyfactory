"""The tests in this file have been adapted from:

https://github.com/crdoconnor/xeger/blob/master/xeger/tests/test_xeger.py
"""

import re
from random import Random
from typing import TYPE_CHECKING, Union

import pytest

from polyfactory.value_generators.regex import RegexFactory

if TYPE_CHECKING:
    from re import Pattern


def match(pattern: Union[str, "Pattern"]) -> None:
    for _ in range(100):
        assert re.match(pattern, RegexFactory(random=Random())(pattern))


def test_single_dot() -> None:
    """Verify that the dot character produces only a single character."""
    match(r"^.$")


def test_dot() -> None:
    """Verify that the dot character doesn't produce newlines.

    See: https://bitbucket.org/leapfrogdevelopment/rstr/issue/1/
    """
    for _ in range(100):
        match(r".+")


def test_date() -> None:
    match(r"^([1-9]|0[1-9]|[12][0-9]|3[01])\D([1-9]|0[1-9]|1[012])\D(19[0-9][0-9]|20[0-9][0-9])$")


def test_up_to_closing_tag() -> None:
    match(r"([^<]*)")


def test_ipv4() -> None:
    match(r"^(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]){3}$")


def test_year_1900_2099() -> None:
    match(r"^(19|20)[\d]{2,2}$")


def test_positive_or_negative_number() -> None:
    match(r"^-{0,1}\d*\.{0,1}\d+$")


def test_positive_integers() -> None:
    match(r"^\d+$")


def test_email_complicated() -> None:
    match(r'^([0-9a-zA-Z]([\+\-_\.][0-9a-zA-Z]+)*)+"@(([0-9a-zA-Z][-\w]*[0-9a-zA-Z]*\.)+[a-zA-Z0-9]{2,17})$')


def test_email() -> None:
    match(r"(.*?)\@(.*?)\.(.*?)")


def test_alpha() -> None:
    match(r"[:alpha:]")


def test_zero_or_more_anything_non_greedy() -> None:
    match(r"(.*?)")


def test_literals() -> None:
    match(r"foo")


def test_digit() -> None:
    match(r"\d")


def test_nondigits() -> None:
    match(r"\D")


def test_literal_with_repeat() -> None:
    match(r"A{3}")


def test_literal_with_range_repeat() -> None:
    match(r"A{2, 5}")


def test_word() -> None:
    match(r"\w")


def test_nonword() -> None:
    match(r"\W")


def test_or() -> None:
    match(r"foo|bar")


def test_or_with_subpattern() -> None:
    match(r"(foo|bar)")


def test_range() -> None:
    match(r"[A-F]")


def test_character_group() -> None:
    match(r"[ABC]")


def test_caret() -> None:
    match(r"^foo")


def test_dollarsign() -> None:
    match(r"foo$")


def test_not_literal() -> None:
    match(r"[^a]")


def test_negation_group() -> None:
    match(r"[^AEIOU]")


def test_lookahead() -> None:
    match(r"foo(?=bar)")


def test_lookbehind() -> None:
    pattern = r"(?<=foo)bar"
    assert re.search(pattern, RegexFactory(random=Random())(pattern))


def test_backreference() -> None:
    match(r"(foo|bar)baz\1")


def test_zero_or_more_greedy() -> None:
    match(r"a*")
    match(r"(.*)")


def test_zero_or_more_non_greedy() -> None:
    match(r"a*?")


@pytest.mark.parametrize("limit", range(5))
def test_incoherent_limit_and_qualifier(limit: int) -> None:
    r = RegexFactory(limit=limit, random=Random())
    o = r(r"a{2}")
    assert len(o) == 2


@pytest.mark.parametrize("seed", [777, 1234, 369, 8031])
def test_regex_factory_object_seeding(seed: int) -> None:
    xg1 = RegexFactory(random=Random(x=seed))
    string1 = xg1(r"\w{3,4}")

    xg2 = RegexFactory(random=Random(x=seed))
    string2 = xg2(r"\w{3,4}")

    assert string1 == string2


def test_regex_factory_random_instance() -> None:
    xg1 = RegexFactory(random=Random())
    xg_random = xg1._random

    xg2 = RegexFactory(random=Random())
    xg2._random = xg_random

    assert xg1._random == xg2._random
    # xg_random is used by both, so if we give
    # the same seed, the result should be the same

    xg_random.seed(90)
    string1 = xg1(r"\w\d\w")
    xg_random.seed(90)
    string2 = xg2(r"\w\d\w")

    assert string1 == string2
