from anchorpoint.textselectors import TextPositionSelector, TextPositionSet

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
