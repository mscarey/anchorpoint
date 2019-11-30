import json
import re

import pytest

from anchorpoint import TextQuoteSelector, TextPositionSelector


class TestTextQuoteSelectors:
    preexisting_material = TextQuoteSelector(
        exact=(
            "protection for a work employing preexisting material in which "
            + "copyright subsists does not extend to any part of the work in "
            + "which such material has been used unlawfully."
        )
    )

    in_no_case = TextQuoteSelector(suffix="idea, procedure,")

    copyright_requires_originality = TextQuoteSelector(suffix="fixed in any tangible")

    amendment_selector = TextQuoteSelector(
        exact="",
        prefix="immunities of citizens of the United States; ",
        suffix=" nor deny to any person",
    )

    def test_convert_selector_to_json(self):
        copyright_dict = self.preexisting_material.dump()
        assert '"exact": "protection for a work' in json.dumps(copyright_dict)

    def test_failed_prefix(self, make_text):
        """
        The phrase "sound recordings" is not in
        the cited subsection, so searching for the interval will fail.
        """
        after_sound = TextQuoteSelector(prefix="sound recordings")
        assert after_sound.as_position(make_text["s102b"]) is None

    def test_failed_suffix(self, make_text):
        up_to_sound = TextQuoteSelector(suffix="sound recordings")
        assert up_to_sound.as_position(make_text["s102b"]) is None

    def test_interval_from_just_prefix(self, make_text):
        """
        The interval should be from the end of the prefix to the end of the
        text passage.

        141 means the string starts at the beginning of a word.
        If it started with 140, there would be a leading space.
        """
        selector = TextQuoteSelector(prefix="method of operation,")
        assert selector.as_position(make_text["s102b"]) == TextPositionSelector(
            141, len(make_text["s102b"])
        )

    def test_exact_from_just_suffix(self, make_text):
        exact = self.in_no_case.select_text(make_text["s102b"])
        assert exact == (
            "In no case does copyright protection for an original "
            + "work of authorship extend to any"
        )

    def test_exact_from_prefix_and_suffix(self, make_text):
        exact = self.amendment_selector.select_text(make_text["amendment"])
        assert exact.startswith("nor shall any State deprive")

    def test_select_text(self, make_text):
        selector = TextQuoteSelector(
            prefix="in no case", exact="does copyright", suffix="protection"
        )
        assert selector.select_text(make_text["s102b"]) == "does copyright"

    def test_select_text_without_exact(self, make_text):
        selector = TextQuoteSelector(prefix="in no case", suffix="protection")
        assert selector.select_text(make_text["s102b"]) == "does copyright"

    def test_rebuilding_from_text(self, make_text):
        new_selector = self.amendment_selector.rebuild_from_text(make_text["amendment"])
        assert new_selector.exact.startswith("nor shall any State deprive")

    def test_failing_to_rebuild_from_text(self):
        new_selector = self.amendment_selector.rebuild_from_text(
            "does not contain selected passages"
        )
        assert not new_selector

    def test_make_position_selector(self, make_text):
        new_selector = self.amendment_selector.as_position(make_text["amendment"])
        assert new_selector.start == make_text["amendment"].find("nor shall any State")

    def test_failing_to_make_position_selector(self):
        new_selector = self.amendment_selector.as_position(
            "does not contain selected passages"
        )
        assert not new_selector

    def test_regex_from_selector_with_just_exact(self):
        selector = TextQuoteSelector(exact="nor shall any State")
        assert selector._passage_regex_without_exact() == r"^.*$"
        assert selector.passage_regex() == r"(nor\ shall\ any\ State)"

    def test_selector_escapes_special_characters(self):
        selector = TextQuoteSelector(suffix=r"opened the C:\documents folder")
        pattern = selector.passage_regex()
        match = re.match(pattern, r"Lee \n opened the C:\documents folder yesterday")
        assert match

    def test_regex_match(self, make_text):
        """
        Comparable to how TextQuoteSelector.exact_from_ends works.

        Provided because double-escaping makes it confusing
        to understand regex patterns constructed by Python.
        """
        pattern = (
            r"immunities\ of\ citizens\ of\ the\ United\ States;"
            + r"\s*(.*?)\s*nor\ deny\ to\ any\ person"
        )
        match = re.search(pattern, make_text["amendment"])
        assert (
            match.group(1)
            == "nor shall any State deprive any person of life, liberty, or property, without due process of law;"
        )

    def test_quote_is_unique(self, make_text):
        assert self.amendment_selector.is_unique_in(make_text["amendment"])

    def test_not_unique_if_absent(self):
        assert not self.amendment_selector.is_unique_in("irrelevant text")

    def test_not_unique_if_appears_twice(self):
        selector = TextQuoteSelector(exact="a")
        assert not selector.is_unique_in("aaaAAAaA")


class TestTextPositionSelectors:
    def test_add_position_selectors(self):
        left = TextPositionSelector(start=5, end=22)
        right = TextPositionSelector(start=12, end=27)
        new = left + right
        assert new.start == 5
        assert new.end == 27

    def test_add_nearly_overlapping_selectors(self):
        left = TextPositionSelector(start=5, end=22)
        right = TextPositionSelector(start=24, end=27)
        new = left + right
        assert new.start == 5
        assert new.end == 27

    def test_adding_nonoverlapping_selectors(self):
        """
        When the selectors aren't near enough to be added,
        the operation returns the selector on the left side.
        """
        left = TextPositionSelector(start=5, end=12)
        right = TextPositionSelector(start=24, end=27)
        new = left + right
        assert new is None

    def test_fail_combining_with_short_text(self):
        left = TextPositionSelector(start=5, end=12)
        right = TextPositionSelector(start=10, end=27)
        text = "This is 26 characters long"
        with pytest.raises(IndexError):
            _ = left.combine(other=right, text=text)

    def test_combine_with_text(self):
        left = TextPositionSelector(start=5, end=12)
        right = TextPositionSelector(start=10, end=26)
        text = "This is 26 characters long"
        new = left.combine(other=right, text=text)
        assert new.end == 26

    def test_dump_position_selector(self):
        selector = TextPositionSelector(start=5, end=12)
        dumped = selector.dump()
        assert dumped["type"] == "TextPositionSelector"

    def test_get_passage_from_position(self, make_text):
        selector = TextPositionSelector(start=53, end=84)
        passage = selector.passage(make_text["amendment"])
        assert passage == "and subject to the jurisdiction"

    def test_fail_to_get_passage_from_position(self, make_text):
        selector = TextPositionSelector(start=53, end=9984)
        with pytest.raises(IndexError):
            _ = selector.passage(make_text["amendment"])

    def test_end_must_be_after_start_position(self):
        with pytest.raises(IndexError):
            _ = TextPositionSelector(start=53, end=14)

    def test_min_start_position_is_0(self):
        selector = TextPositionSelector(start=-3, end=84)
        assert selector.start == 0

    def test_convert_position_to_quote(self, make_text):
        selector = TextPositionSelector(start=53, end=84)
        quote = selector.as_quote_selector(make_text["amendment"])
        assert quote.exact == "and subject to the jurisdiction"
        assert quote.prefix.strip().endswith("ates")
        assert quote.suffix.strip().startswith("ther")

    def test_make_quote_selector_from_entire_text(self):
        passage = "entire passage"
        interval = TextPositionSelector(0, len(passage))
        quote = interval.as_quote_selector(passage)
        assert quote.exact == "entire passage"
        assert not quote.prefix
        assert not quote.suffix

    def test_fail_to_make_quote_selector(self):
        passage = "too short"
        interval = TextPositionSelector(50, 100)
        with pytest.raises(IndexError):
            _ = interval.as_quote_selector(passage)