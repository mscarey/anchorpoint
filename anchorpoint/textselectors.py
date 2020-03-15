"""
Text substring selectors for anchoring annotations.

Based on parts of the W3C `Web Annotation Data
Model <https://www.w3.org/TR/annotation-model/>`_.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from typing import Optional, Tuple

from anchorpoint.utils.ranges import Range, RangeSet, _InfiniteValue


@dataclass(frozen=True)
class TextQuoteSelector:
    """
    Describes a textual segment by quoting it, or passages before or after it.

    Based on the Web Annotation Data Model `Text Quote Selector
    <https://www.w3.org/TR/annotation-model/#text-quote-selector>`_ standard

    :param exact:
        a copy of the text which is being selected

    :param prefix:
        a snippet of text that occurs immediately before the text which
        is being selected.

    :param suffix:
        the snippet of text that occurs immediately after the text which
        is being selected.

    """

    exact: str = ""
    prefix: str = ""
    suffix: str = ""

    def find_match(self, text: str) -> Optional[re.Match]:
        """
        Get the first match for the selector within a string.

        :param text:
            text to search for a match to the selector

        :returns:
            a regular expression match, or None
        """
        pattern = self.passage_regex()
        return re.search(pattern, text, re.IGNORECASE)

    def select_text(self, text: str) -> Optional[str]:
        """
        Get the passage matching the selector, minus any whitespace.

        :param text:
            the passage where an exact quotation needs to be located.

        :returns:
            the passage between :attr:`prefix` and :attr:`suffix` in ``text``.
        """
        match = self.find_match(text)
        if match:
            return match.group(1).strip()
        return None

    def rebuild_from_text(self, text: str) -> Optional[TextQuoteSelector]:
        """
        Make new selector with the "exact" value found in a given text.

        Used for building a complete selector when :attr:`exact` has not
        been specified.

        :param text:
            the passage where an exact quotation needs to be located

        :returns:
            a new selector with the "exact" value found in the provided text
        """
        exact = self.select_text(text)
        if not exact:
            return None
        return TextQuoteSelector(exact=exact, prefix=self.prefix, suffix=self.suffix)

    def dump(self):
        """Serialize the selector."""
        return {
            "type": "TextQuoteSelector",
            "exact": self.exact,
            "prefix": self.prefix,
            "suffix": self.suffix,
        }

    def as_position(self, text: str) -> Optional[TextPositionSelector]:
        """
        Get the interval where the selected quote appears in "text".

        :param text:
            the passage where an exact quotation needs to be located

        :returns:
            the position selector for the location of the exact quotation
        """
        match = self.find_match(text)
        if match:
            # Getting indices from match group 1 (in the parentheses),
            # not match 0 which includes prefix and suffix
            return TextPositionSelector(match.start(1), match.end(1))
        return None

    def is_unique_in(self, text: str) -> bool:
        """
        Test if selector refers to exactly one passage in text.

        :param text:
            the passage where an exact quotation needs to be located

        :returns:
            whether the passage appears exactly once
        """
        match = self.find_match(text)
        if match:
            second_match = self.find_match(text[match.end(1) :])
            return not bool(second_match)
        return False

    def _passage_regex_without_exact(self) -> str:
        """Get regex for the passage given the "exact" parameter is missing."""

        if not (self.prefix or self.suffix):
            return r"^.*$"

        if not self.prefix:
            return r"^(.*)" + self.suffix_regex()

        if not self.suffix:
            return self.prefix_regex() + r"(.*)$"

        return (self.prefix_regex() + r"(.*)" + self.suffix_regex()).strip()

    def passage_regex(self):
        """Get regex to identify the selected text."""

        if not self.exact:
            return self._passage_regex_without_exact()

        return (
            self.prefix_regex()
            + r"("
            + re.escape(self.exact)
            + r")"
            + self.suffix_regex()
        ).strip()

    def prefix_regex(self):
        """Get regex for the text before any whitespace and the selection."""
        return (re.escape(self.prefix.strip()) + r"\s*") if self.prefix else ""

    def suffix_regex(self):
        """Get regex for the text following the selection and any whitespace."""
        return (r"\s*" + re.escape(self.suffix.strip())) if self.suffix else ""


@dataclass(frozen=True)
class TextPositionSelector(Range):
    """
    Describes a textual segment by start and end positions.

    Based on the Web Annotation Data Model `Text Position Selector
    <https://www.w3.org/TR/annotation-model/#text-position-selector>`_ standard

    :param start:
        The starting position of the segment of text.
        The first character in the full text is character position 0,
        and the character is included within the segment.

    :param end:
        The end position of the segment of text.
        The character is not included within the segment.
    """

    start: int = 0
    end: Optional[int] = _InfiniteValue(negative=False)
    include_start: bool = True
    include_end: bool = False

    def __post_init__(self):
        if self.start < 0:
            object.__setattr__(self, "start", 0)
        if self.end:
            if self.end <= self.start:
                raise IndexError(
                    "End position must be a positive number "
                    "greater than the start position"
                )

    def __add__(self, other: TextPositionSelector) -> Optional[TextPositionSelector]:
        """
        Make a new selector covering the combined ranges of self and other.

        :param other:
            selector for another text interval

        :param margin:
            allowable distance between two selectors that can still be added together

        :returns:
            a selector reflecting the combined range if possible, otherwise None
        """
        return self | other

    def as_quote_selector(self, text: str) -> TextQuoteSelector:
        """
        Make a quote selector, adding prefix and suffix if possible.

        :param text:
            the passage where an exact quotation needs to be located
        """
        exact = text[self.start : self.end]
        margins = 0
        end = self.end or len(text)
        while margins < (len(text) - len(exact)):
            margins += 5
            prefix = text[max(0, self.start - margins) : self.start]
            suffix = text[end : min(len(text), end + margins)]
            new_selector = TextQuoteSelector(exact=exact, prefix=prefix, suffix=suffix)
            if new_selector.is_unique_in(text):
                return new_selector
        return TextQuoteSelector(
            exact=exact, prefix=text[: self.start], suffix=text[self.end :]
        )

    def combine(self, other: TextPositionSelector, text: str):
        """Make new selector combining ranges of self and other if it will fit in text."""
        for selector in (self, other):
            selector.validate(text)
        return self + other

    def dump(self):
        """Serialize the selector."""
        return {"type": "TextPositionSelector", "start": self.start, "end": self.end}

    def passage(self, text: str) -> str:
        """Get the quotation from text identified by start and end positions."""
        self.validate(text)
        return text[self.start : self.end]

    def validate(self, text: str) -> None:
        """Verify that selector's text positions exist in text."""
        if self.end and self.end > len(text):
            raise IndexError(
                f'Text "{text}" is too short to include '
                + f"the interval ({self.start}, {self.end})"
            )
        return None


class TextPositionSet(RangeSet):
    pass
