from anchorpoint.textselectors import (
    TextPositionSelector,
    TextPositionSet,
    TextQuoteSelector,
)

import pytest


class TestSelectorSet:
    def test_make_selector_set(self):
        quotes = [
            TextPositionSelector(start=5, end=10),
            TextPositionSelector(start=20, end=30),
        ]
        group = TextPositionSet(quotes)
        new_group = group + TextPositionSelector(start=2, end=8)
        assert new_group.ranges()[0].end == 10
        assert new_group.ranges()[1].start == 20

    def test_subtract_from_selector_set(self):
        quotes = [
            TextPositionSelector(start=5, end=10),
            TextPositionSelector(start=20, end=30),
        ]
        group = TextPositionSet(quotes)
        new_group = group - 5
        assert new_group.ranges()[0].start == 0
        assert new_group.ranges()[0].end == 5

    def test_subtract_too_much_from_selector_set(self):
        quotes = [
            TextPositionSelector(start=5, end=10),
            TextPositionSelector(start=20, end=30),
        ]
        group = TextPositionSet(quotes)
        with pytest.raises(ValueError):
            _ = group - 10

    def test_make_set_from_one_selector(self):
        quote = TextPositionSelector(start=5, end=10)
        group = TextPositionSet(quote)
        assert group.ranges()[0].start == 5

    def test_string_for_set(self):
        quote = TextPositionSelector(start=5, end=10)
        group = TextPositionSet(quote)
        assert str(group).startswith("TextPositionSet([TextPositionSelector")

    def test_subtract_set(self, make_text):
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
