from __future__ import annotations

from typing import List, Optional, Sequence, Union


class TextPassage:
    """
    A contiguous passage of text.

    :param text:
        the text content of the contiguous passage
    """

    def __repr__(self):
        return f'TextPassage("{self.text}")'

    def __init__(self, text: str):
        self.text = text

    def means(self, other: Optional[TextPassage]) -> bool:
        if other is None:
            return False
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"Cannot compare {self.__class__.__name__} and {other.__class__.__name__} for same meaning."
            )

        return self.text.strip(",:;. ") == other.text.strip(",:;. ")

    def __ge__(self, other: Optional[TextPassage]) -> bool:
        if not other:
            return True
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"Cannot compare {self.__class__.__name__} and {other.__class__.__name__} for implication."
            )
        other_text = other.text.strip(",:;. ")
        return other_text in self.text

    def __gt__(self, other: Optional[TextPassage]) -> bool:
        return self >= other and not self.means(other)


class TextSequence(Sequence[Union[None, TextPassage]]):
    """
    Sequential passages of text that need not be consecutive.

    Unlike a `Legislice <https://legislice.readthedocs.io/>`__ Enactment, a
    TextSequence does not preserve the tree structure
    of the quoted document.

    :param passages:
        the text passages included in the TextSequence, which should be chosen
        to express a coherent idea. "None"s in the sequence represent spans of
        text that exist in the source document, but that haven't been chosen
        to be part of the TextSequence.
    """

    def __init__(self, passages: List[Optional[TextPassage]] = None):
        self.passages = passages or []

    def __repr__(self):
        return f"TextSequence({self.passages})"

    def __len__(self):
        return len(self.passages)

    def __getitem__(self, key):
        return self.passages[key]

    def __str__(self):
        result = ""
        for phrase in self.passages:
            if phrase is None:
                if not result.endswith("…"):
                    result += "…"
            else:
                if result and not result.endswith(("…", " ")):
                    result += " "
                result += phrase.text
        if result == "…":
            return ""
        return result

    def __ge__(self, other: TextSequence):
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"Cannot compare {self.__class__.__name__} and {other.__class__.__name__} for implication."
            )
        for other_passage in other.passages:
            if not any(
                (
                    (other_passage is None)
                    or (self_passage and self_passage >= other_passage)
                )
                for self_passage in self.passages
            ):
                return False
        return True

    def __gt__(self, other: TextSequence):
        if self.means(other):
            return False
        return self >= other

    def __add__(self, other: TextSequence) -> TextSequence:
        r"""Combine TextSequences by merging their selected :class:`TextPassage`\s."""
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"Cannot add class {self.__class__.__name__} to any other object type."
            )
        if not other.passages:
            return self
        if not self.passages:
            return other
        if other.passages[0] is self.passages[-1] is None:
            return TextSequence(self.passages[:-1] + other.passages)
        return TextSequence(self.passages + other.passages)

    def strip(self) -> TextSequence:
        """Remove symbols representing missing text from the beginning and end."""
        result = self.passages.copy()
        if result and result[0] is None:
            result = result[1:]
        if result and result[-1] is None:
            result = result[:-1]
        return TextSequence(result)

    def means(self, other: TextSequence) -> bool:
        """Test if all the passages in self and other correspond with each other."""
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"Cannot compare {self.__class__.__name__} and {other.__class__.__name__} for same meaning."
            )
        self_passages = self.strip().passages
        other_passages = other.strip().passages
        if len(self_passages) != len(other_passages):
            return False

        zipped = zip(self_passages, other_passages)
        return all(
            pair[0].means(pair[1]) if pair[0] is not None else pair[1] is None
            for pair in zipped
        )
