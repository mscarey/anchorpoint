from anchorpoint.schemas import TextPositionSetFactory
from anchorpoint.textselectors import (
    TextPositionSelector,
    TextPositionSet,
    TextQuoteSelector,
)

import pytest


class TestMakeSelectorSet:
    def test_make_selector_set_from_different_selectors(self):
        quotes = [
            TextPositionSelector(start=0, end=7),
            TextQuoteSelector(exact="great"),
        ]
        factory = TextPositionSetFactory(passage="Here is some great text.")
        selector_set = factory.from_selection(quotes)
        assert selector_set.ranges()[0].end == 7
        assert selector_set.ranges()[1].start == 13

    def test_make_selector_set_from_exact_strings(self):
        quotes = ["some", "text"]
        factory = TextPositionSetFactory(passage="Here is some great text.")
        selector_set = factory.from_exact_strings(quotes)
        assert selector_set.ranges()[0].start == 8
        assert selector_set.ranges()[1].start == 19

    def test_make_selector_set_from_one_string(self):
        quote = "Here is some"
        factory = TextPositionSetFactory(passage="Here is some great text.")
        selector_set = factory.from_selection(quote)
        assert selector_set.ranges()[0].start == 0
        assert selector_set.ranges()[0].end == 12

    def test_make_selector_set_from_factory(self):
        quotes = [
            TextPositionSelector(start=5, end=10),
            TextPositionSelector(start=20, end=30),
        ]
        group = TextPositionSet(quotes)
        new_group = group + TextPositionSelector(start=2, end=8)
        assert new_group.ranges()[0].end == 10
        assert new_group.ranges()[1].start == 20

    def test_make_selector_set_with_selector_from_string(self):
        group = TextPositionSet("[5, 10)")
        assert group.ranges()[0].start == 5

    def test_make_selector_set_from_position_selector(self):
        factory = TextPositionSetFactory(passage="Here is some great text.")
        position_set = factory.from_selection(TextPositionSelector(start=5, end=10))
        assert position_set.ranges()[0].start == 5

    def test_make_selector_set_from_list_of_strings(self):
        factory = TextPositionSetFactory(passage="Here is some great text.")
        position_set = factory.from_selection(["Here is some", "text."])
        assert position_set.ranges()[0].start == 0
        assert position_set.ranges()[0].end == 12

    def test_make_selector_set_from_True(self):
        passage = "Here is some great text."
        factory = TextPositionSetFactory(passage=passage)
        position_set = factory.from_selection(True)
        assert position_set.as_string(text=passage) == "Here is some great text."

    def test_make_selector_set_from_False(self):
        passage = "Here is some great text."
        factory = TextPositionSetFactory(passage=passage)
        position_set = factory.from_selection(False)
        assert position_set.as_string(text=passage) == ""

    def test_selector_set_repr(self):
        group = TextPositionSet("[5, 10)")
        assert repr(group).startswith("TextPositionSet")


class TestCombineSelectorSet:
    def test_subtract_int_from_selector_set(self):
        quotes = [
            TextPositionSelector(start=5, end=10),
            TextPositionSelector(start=20, end=30),
        ]
        group = TextPositionSet(quotes)
        new_group = group - 5
        assert new_group.ranges()[0].start == 0
        assert new_group.ranges()[0].end == 5

    def test_add_int_to_selector_set(self):
        quotes = [
            TextPositionSelector(start=5, end=10),
            TextPositionSelector(start=20, end=30),
        ]
        group = TextPositionSet(quotes)
        new_group = group + 5
        assert new_group.ranges()[0].start == 10
        assert new_group.ranges()[0].end == 15

    def test_error_add_negative_int_to_selector_set(self):
        quotes = [
            TextPositionSelector(start=5, end=10),
            TextPositionSelector(start=20, end=30),
        ]
        group = TextPositionSet(quotes)
        with pytest.raises(IndexError):
            _ = group + -15

    def test_subtract_too_much_from_selector_set(self):
        quotes = [
            TextPositionSelector(start=5, end=10),
            TextPositionSelector(start=20, end=30),
        ]
        group = TextPositionSet(quotes)
        with pytest.raises(IndexError):
            _ = group - 40

    def test_make_set_from_one_selector(self):
        quote = TextPositionSelector(start=5, end=10)
        group = TextPositionSet(quote)
        assert group.ranges()[0].start == 5

    def test_string_for_set(self):
        quote = TextPositionSelector(start=5, end=10)
        group = TextPositionSet(quote)
        assert str(group).startswith("TextPositionSet([TextPositionSelector")

    def test_add_non_overlapping_sets(self):
        left = TextPositionSet(TextPositionSelector(start=50, end=60))
        right = TextPositionSet(TextPositionSelector(start=20, end=40))
        new = left + right
        assert isinstance(new, TextPositionSet)
        assert isinstance(new.ranges()[0], TextPositionSelector)
        assert len(new.ranges()) == 2
        assert new.ranges()[0].start == 20

    def test_add_overlapping_sets(self):
        left = TextPositionSet(TextPositionSelector(start=40, end=60))
        right = TextPositionSet(TextPositionSelector(start=50, end=80))
        new = left + right
        assert isinstance(new, TextPositionSet)
        new_ranges = new.ranges()
        assert isinstance(new_ranges[0], TextPositionSelector)
        assert len(new_ranges) == 1
        assert new_ranges[0].start == 40
        assert new_ranges[0].end == 80

    def test_add_selector_to_set(self):
        left = TextPositionSet(TextPositionSelector(start=50, end=60))
        right = TextPositionSelector(start=20, end=40)
        new = left + right
        assert isinstance(new, TextPositionSet)
        assert isinstance(new.ranges()[0], TextPositionSelector)
        assert len(new.ranges()) == 2
        assert new.ranges()[0].start == 20

    def test_add_set_to_selector(self):
        left = TextPositionSelector(start=40, end=60)
        right = TextPositionSet(TextPositionSelector(start=20, end=35))
        new = left + right
        assert isinstance(new, TextPositionSet)
        assert isinstance(new.ranges()[0], TextPositionSelector)
        assert len(new.ranges()) == 2
        assert new.ranges()[0].start == 20

    def test_subtract_set_from_set(self, make_text):
        s102b = make_text["s102b"]
        selector = TextQuoteSelector(suffix=", procedure")
        position = selector.as_position(s102b)
        selector_set = TextPositionSet(position)

        to_subtract = TextQuoteSelector(exact="for an original work of authorship")
        position_to_subtract = to_subtract.as_position(s102b)
        set_to_subtract = TextPositionSet(position_to_subtract)

        new_set = selector_set - set_to_subtract

        assert new_set.ranges()[0].start == 0
        assert new_set.ranges()[1].start == 71

        assert isinstance(new_set, TextPositionSet)
        assert isinstance(new_set.ranges()[0], TextPositionSelector)

    def test_intersection_of_set_and_selector(self, make_text):
        s102b = make_text["s102b"]
        selector = TextQuoteSelector(suffix=", procedure")
        position = selector.as_position(s102b)
        selector_set = TextPositionSet(position)
        selector = TextPositionSelector(start=70, end=100)
        combined = selector_set & selector
        assert combined.ranges()[0].start == 70
        assert combined.ranges()[0].end == 90
        assert isinstance(combined, TextPositionSet)

    def test_union_of_set_and_selector(self, make_text):
        s102b = make_text["s102b"]
        selector = TextQuoteSelector(suffix=", procedure")
        position = selector.as_position(s102b)
        selector_set = TextPositionSet(position)
        selector = TextPositionSelector(start=70, end=100)
        combined = selector_set | selector
        assert combined.ranges()[0].start == 0
        assert combined.ranges()[0].end == 100
        assert isinstance(combined, TextPositionSet)

    def test_make_quote_selectors_from_set(self, make_text):
        quote = TextQuoteSelector(exact="United States", suffix=" and subject")
        position = quote.as_position(make_text["amendment"])
        position_set = TextPositionSet(position)
        new_quotes = position_set.as_quotes(make_text["amendment"])
        assert new_quotes[0].exact == "United States"
        assert new_quotes[0].prefix.strip().endswith("in the")


class TestCompareSelectorSet:
    def test_full_passage_implies_selections(self, make_text):
        passage = make_text["s102b"]
        factory = TextPositionSetFactory(passage=passage)
        selector_set = factory.from_quote_selectors(
            [
                TextQuoteSelector(exact="In no case does copyright protection"),
                TextQuoteSelector(exact="extend to any idea"),
            ]
        )
        full_passage = TextPositionSet([TextPositionSelector(0, 200)])
        assert full_passage > selector_set

    def test_not_greater_than_regular_set(self):
        full_passage = TextPositionSet([TextPositionSelector(0, 200)])
        regular_set = set()
        assert not full_passage > regular_set

    def test_add_blank_margin(self):
        selector_set = TextPositionSet(
            [TextPositionSelector(0, 4), TextPositionSelector(5, 10)]
        )
        passage = "Some text."
        assert selector_set.as_string(text=passage) == "Some…text."
        result = selector_set.add_margin(text=passage, margin_width=1)
        assert result.as_string(text=passage) == "Some text."

    def test_cannot_add_negative_margin(self):
        passage = "Some text."
        selector_set = TextPositionSet(
            [TextPositionSelector(0, 4), TextPositionSelector(5, 10)]
        )
        with pytest.raises(ValueError):
            selector_set.add_margin(text=passage, margin_width=-1)

    def test_add_margin_with_characters(self):
        selector_set = TextPositionSet(
            [TextPositionSelector(0, 7), TextPositionSelector(11, 21)]
        )
        passage = 'a quote.") Therefore,'
        assert selector_set.as_string(text=passage) == "a quote…Therefore,"
        result = selector_set.add_margin(text=passage, margin_width=4)
        assert result.as_string(text=passage) == 'a quote.") Therefore,'


class TestTextFromSelectorSet:
    def test_get_text_selection_from_set(self, make_text):
        passage = make_text["s102b"]
        factory = TextPositionSetFactory(passage=passage)
        selector_set = factory.from_quote_selectors(
            [
                TextQuoteSelector(exact="In no case does copyright protection"),
                TextQuoteSelector(exact="extend to any idea"),
            ]
        )
        result = selector_set.as_string(text=passage)
        assert result == "In no case does copyright protection…extend to any idea…"
