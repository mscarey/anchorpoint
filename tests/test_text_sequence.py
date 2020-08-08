from tests.conftest import make_text
from typing import Type
import pytest

from anchorpoint.textselectors import (
    TextPositionSet,
    TextQuoteSelector,
    TextPositionSelector,
)
from anchorpoint.schemas import TextPositionSetFactory
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


class TestCompareTextSequence:
    def test_same_meaning_regardless_of_leading_ellipsis(self, make_text):
        passage = make_text["s102b"]
        factory = TextPositionSetFactory(passage=passage)
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

    def test_one_sequence_means_another(self, make_text):
        passage = make_text["s102b"]
        factory = TextPositionSetFactory(passage=passage)
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
        factory = TextPositionSetFactory(passage=passage)
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
        factory = TextPositionSetFactory(passage=passage)
        selector_set = factory.from_quote_selectors(
            [
                TextQuoteSelector(exact="In no case does copyright protection"),
                TextQuoteSelector(exact="extend to any idea"),
            ]
        )
        full_passage = TextPositionSet([TextPositionSelector(0, 200)])

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


class TestTextSequenceString:
    def test_text_sequence_with_only_blanks(self):
        blanks = TextSequence([None, None])
        assert blanks[1] is None
        assert len(blanks) == 2
        assert str(blanks) == ""
