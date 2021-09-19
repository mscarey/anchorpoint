import pytest

from anchorpoint.textselectors import (
    TextPositionSet,
    TextQuoteSelector,
    TextPositionSelector,
)
from anchorpoint.textselectors import TextPositionSetFactory
from anchorpoint.textsequences import TextPassage, TextSequence


class TestCompareTextPassage:
    def test_greater_than_None(self):
        words = TextPassage("words")
        assert words >= None
        assert words > None

    def test_does_not_mean_None(self):
        words = TextPassage("words")
        assert not words.means(None)

    def test_cannot_compare_to_TextSequence(self):
        words = TextPassage("words")
        with pytest.raises(TypeError):
            words >= TextSequence(["words", "more words"])

    def test_cannot_check_name_meaning_with_TextSequence(self):
        words = TextPassage("words")
        with pytest.raises(TypeError):
            words.means(TextSequence(["words", "more words"]))


class TestCreateTextSequence:
    def test_no_extra_None_when_creating_sequence_from_position_selector(self):
        """Test zero indexing bug, length not same as index of last character."""
        passage = "A short passage."
        factory = TextPositionSetFactory(text=passage)
        selector_set = factory.from_selection(TextPositionSelector(start=0, end=16))
        sequence = selector_set.as_text_sequence(passage)
        assert len(sequence) == 1
        assert str(sequence) == "A short passage."

    def test_blank_text_sequence_string(self):
        sequence = TextSequence()
        assert str(sequence) == ""

    def test_select_from_no_content(self):
        selector_set = TextPositionSet(
            positions=[TextPositionSelector(start=5, end=10)]
        )
        sequence = selector_set.as_text_sequence("")
        assert len(sequence) == 0
        assert str(sequence) == ""

    def test_select_nothing_from_no_content(self):
        selector_set = TextPositionSet()
        sequence = selector_set.as_text_sequence("")
        assert len(sequence) == 0
        assert str(sequence) == ""

    def test_select_from_start_of_passage(self):
        selector_set = TextPositionSet(
            positions=TextPositionSelector(start=0, end=4),
        )
        sequence = selector_set.as_text_sequence("Some text.")
        assert str(sequence) == "Some…"

    def test_select_after_start_of_passage(self):
        selector_set = TextPositionSet(
            positions=[TextPositionSelector(start=5, end=10)],
        )
        sequence = selector_set.as_text_sequence("Some text.")
        assert str(sequence) == "…text."
        assert repr(sequence) == 'TextSequence([None, TextPassage("text.")])'

    def test_correct_end_index_when_creating_sequence_from_True(self):
        """Test zero indexing bug, length not same as index of last character."""
        passage = "A short passage."
        factory = TextPositionSetFactory(text=passage)
        selector_set = factory.from_selection(True)
        ranges = selector_set.ranges()
        assert ranges[0].start == 0
        assert ranges[0].end == 16
        assert ranges[0].include_end is False


class TestCompareTextSequence:
    def test_same_meaning_regardless_of_leading_ellipsis(self, make_text):
        passage = make_text["s102b"]
        factory = TextPositionSetFactory(text=passage)
        selector_set = factory.from_quote_selectors(
            [
                TextQuoteSelector(exact="In no case does copyright protection"),
                TextQuoteSelector(exact="extend to any idea"),
            ]
        )
        passages_as_sequence = selector_set.as_text_sequence(passage)
        handcrafted_sequence = TextSequence(
            passages=[
                None,
                TextPassage("In no case does copyright protection"),
                None,
                TextPassage("extend to any idea"),
            ]
        )
        assert passages_as_sequence.means(handcrafted_sequence)
        assert not passages_as_sequence > handcrafted_sequence

    def test_same_meaning_comparing_text_to_none(self):
        first_sequence = TextSequence(
            passages=[
                None,
                TextPassage("In no case does copyright protection"),
                None,
                TextPassage("extend to any idea"),
                None,
            ]
        )
        second_sequence = TextSequence(
            passages=[
                None,
                TextPassage("In no case does copyright protection"),
                TextPassage("of a college memoir"),
                TextPassage("extend to any idea"),
                None,
            ]
        )

        assert not first_sequence.means(second_sequence)
        assert second_sequence > first_sequence

    def test_one_sequence_means_another(self, make_text):
        passage = make_text["s102b"]
        factory = TextPositionSetFactory(text=passage)
        selector_set = factory.from_quote_selectors(
            [
                TextQuoteSelector(exact="In no case does copyright protection"),
                TextQuoteSelector(exact="extend to any idea"),
            ]
        )
        passages_as_sequence = selector_set.as_text_sequence(passage)
        handcrafted_sequence = TextSequence(
            passages=[
                TextPassage("In no case does copyright protection"),
                None,
                TextPassage("extend to any idea"),
            ]
        )
        assert passages_as_sequence.means(handcrafted_sequence)
        assert not passages_as_sequence > handcrafted_sequence

    def test_omitting_None_from_sequence_changes_meaning(self, make_text):
        passage = make_text["s102b"]
        factory = TextPositionSetFactory(text=passage)
        selector_set = factory.from_quote_selectors(
            [
                TextQuoteSelector(exact="In no case does copyright protection"),
                TextQuoteSelector(exact="extend to any idea"),
            ]
        )
        passages_as_sequence = selector_set.as_text_sequence(passage)
        handcrafted_sequence = TextSequence(
            passages=[
                TextPassage("In no case does copyright protection"),
                TextPassage("extend to any idea"),
            ]
        )
        assert (
            str(passages_as_sequence)
            == "In no case does copyright protection…extend to any idea…"
        )
        assert (
            str(handcrafted_sequence)
            == "In no case does copyright protection extend to any idea"
        )
        assert not passages_as_sequence.means(handcrafted_sequence)

    def test_full_passage_implies_selections(self, make_text):
        passage = make_text["s102b"]
        factory = TextPositionSetFactory(text=passage)
        selector_set = factory.from_quote_selectors(
            [
                TextQuoteSelector(exact="In no case does copyright protection"),
                TextQuoteSelector(exact="extend to any idea"),
            ]
        )
        full_passage = TextPositionSet(
            positions=[TextPositionSelector(start=0, end=200)]
        )

        passages_as_sequence = selector_set.as_text_sequence(passage)
        full_passage_as_sequence = full_passage.as_text_sequence(passage)
        assert full_passage_as_sequence > passages_as_sequence
        assert not passages_as_sequence > full_passage_as_sequence

    def test_cannot_compare_to_TextPassage(self):
        words = TextPassage("words")
        with pytest.raises(TypeError):
            TextSequence(["words", "more words"]) >= words

    def test_cannot_check_name_meaning_with_TextSequence(self):
        words = TextPassage("words")
        with pytest.raises(TypeError):
            TextSequence(["words", "more words"]).means(words)


class TestAddTextSequence:
    def test_handle_Nones_at_beginning_and_end(self):
        handcrafted_sequence = TextSequence(
            passages=[
                TextPassage("In no case does copyright protection"),
                None,
                TextPassage("extend to any idea"),
                None,
            ]
        )
        second_sequence = TextSequence(
            passages=[None, TextPassage("embodied in such work.")]
        )
        new_sequence = handcrafted_sequence + second_sequence
        assert new_sequence[1] is None
        assert new_sequence[2] is not None

        assert (
            str(new_sequence)
            == "In no case does copyright protection…extend to any idea…embodied in such work."
        )

    def test_add_without_Nones(self):
        sequence = TextSequence(passages=[TextPassage("This is a full section.")])
        second_sequence = TextSequence(
            passages=[TextPassage("This is the full immediately following section.")]
        )
        new_sequence = sequence + second_sequence
        len(new_sequence) == 2
        assert (
            str(new_sequence)
            == "This is a full section. This is the full immediately following section."
        )

    def test_add_tempty_TextSequences(self):
        left = TextSequence(passages=[TextPassage("Some Text.")])
        right = TextSequence([])
        assert left + right == left

    def test_add_to_empty_TextSequences(self):
        left = TextSequence()
        right = TextSequence(passages=[TextPassage("Some Text.")])
        assert left + right == right

    def test_add_sequence_and_None(self):
        left = TextSequence(passages=[TextPassage("Some Text.")])
        with pytest.raises(TypeError):
            left + None


class TestTextSequenceString:
    def test_text_sequence_with_only_blanks(self):
        blanks = TextSequence([None, None])
        assert blanks[1] is None
        assert len(blanks) == 2
        assert str(blanks) == ""
