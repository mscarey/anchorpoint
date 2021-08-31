"""
Text substring selectors for anchoring annotations.

Based on parts of the W3C `Web Annotation Data
Model <https://www.w3.org/TR/annotation-model/>`_.
"""

from __future__ import annotations

import re

from typing import List, Optional, Tuple, Union

from anchorpoint.textsequences import TextPassage, TextSequence
from anchorpoint.utils._helper import InfiniteValue, Inf
from anchorpoint.utils.ranges import Range, RangeSet
from pydantic import BaseModel, validator, root_validator


class TextSelectionError(Exception):
    """Exception for failing to select text as described by user."""

    pass


class TextQuoteSelector(BaseModel):
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

    @staticmethod
    def split_anchor_text(text: str) -> Tuple[str, ...]:
        """
        Break up shorthand text selector format into three fields.

        Tries to break up the  string into :attr:`~TextQuoteSelector.prefix`,
        :attr:`~TextQuoteSelector.exact`,
        and :attr:`~TextQuoteSelector.suffix`, by splitting on exactly two pipe characters.

        :param text: a string or dict representing a text passage
        :returns: a tuple of the three values
        """

        if text.count("|") == 0:
            return ("", text, "")
        elif text.count("|") == 2:
            return tuple([*text.split("|")])
        raise TextSelectionError(
            "If the 'text' field includes | pipe separators, it must contain exactly "
            "two, separating the string into 'prefix', 'exact', and 'suffix'."
        )

    @classmethod
    def from_text(cls, text: str) -> TextQuoteSelector:
        """
        Create a selector from a text string.

        "prefix" and "suffix" fields may be created by separating part
        of the text with a pipe character ("|").

        :param text:
            the passage where an exact quotation needs to be located

        :returns:
            a selector for the location of the exact quotation

        >>> text = "process, system,|method of operation|, concept, principle"
        >>> selector = TextQuoteSelector.from_text(text)
        >>> selector.prefix
        'process, system,'
        >>> selector.exact
        'method of operation'
        >>> selector.suffix
        ', concept, principle'

        """
        split_text = cls.split_anchor_text(text)
        return cls(prefix=split_text[0], exact=split_text[1], suffix=split_text[2])

    def find_match(self, text: str) -> Optional[re.Match]:
        """
        Get the first match for the selector within a string.

        :param text:
            text to search for a match to the selector

        :returns:
            a regular expression match, or None

        >>> text = "process, system, method of operation, concept, principle"
        >>> selector = TextQuoteSelector(exact="method of operation")
        >>> selector.find_match(text)
        <re.Match object; span=(17, 36), match='method of operation'>
        """
        pattern = self.passage_regex()
        return re.search(pattern, text, re.IGNORECASE)

    def select_text(self, text: str) -> Optional[str]:
        """
        Get the passage matching the selector, minus any whitespace at ends.

        :param text:
            the passage where an exact quotation needs to be located.

        :returns:
            the passage between :attr:`prefix` and :attr:`suffix` in ``text``.

        >>> text = "process, system, method of operation, concept, principle"
        >>> selector = TextQuoteSelector(prefix="method of operation,")
        >>> selector.select_text(text)
        'concept, principle'
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

    def as_position(self, text: str) -> TextPositionSelector:
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
            return TextPositionSelector(start=match.start(1), end=match.end(1))
        text_sample = text[:100] + "..." if len(text) > 100 else text
        raise TextSelectionError(
            f'Unable to find pattern "{self.passage_regex()}" in text: "{text_sample}"'
        )

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
            return r"^(.*?)" + self.suffix_regex()

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


class TextPositionSelector(BaseModel):
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
    end: Optional[int] = None

    @classmethod
    def from_range(cls, range: Range) -> TextPositionSelector:
        if isinstance(range.end, InfiniteValue):
            end = None
        else:
            end = range.end
        return TextPositionSelector(start=range.start, end=end)

    @validator("start", allow_reuse=True)
    def start_not_negative(cls, v) -> bool:
        """
        Check if start position is not negative.

        :returns:
            whether the start position is not negative
        """
        if v < 0:
            raise IndexError("Start position for text range cannot be negative.")
        return v

    @root_validator(allow_reuse=True)
    def start_less_than_end(cls, values):
        start, end = values.get("start"), values.get("end")
        if end is not None and end <= start:
            raise IndexError("End position must be greater than start position.")
        return values

    def range(self) -> Range:
        """Get the range of the text."""
        return Range(start=self.start, end=self.end or Inf)

    def rangeset(self) -> RangeSet:
        """Get the range set of the text."""
        return RangeSet([self.range()])

    def __add__(
        self, value: TextPositionSelector
    ) -> Optional[Union[TextPositionSelector, TextPositionSet]]:
        """
        Make a new selector covering the combined ranges of self and other.

        :param other:
            selector for another text interval

        :param margin:
            allowable distance between two selectors that can still be added together

        :returns:
            a selector reflecting the combined range if possible, otherwise None
        """
        if not isinstance(value, int):
            return self | value

        if self.start + value < 0:
            raise IndexError(
                f"Adding {value} to ({self.start}, {self.end}) "
                "would result in a negative start position."
            )

        if self.end is None:
            new_end = self.end
        else:
            new_end = self.end + value

        return TextPositionSelector(start=self.start + value, end=new_end)

    def __or__(
        self, other: Union[TextPositionSelector, TextPositionSet, Range, RangeSet]
    ) -> Union[TextPositionSelector, TextPositionSet]:
        """
        Make a new selector covering the combined ranges of self and other.

        :param other:
            selector for another text interval

        :returns:
            a selector reflecting the combined range
        """
        if isinstance(other, (TextPositionSelector, TextPositionSet)):
            other = other.rangeset()

        new_rangeset = self.rangeset() | other

        new_ranges = new_rangeset.ranges()
        if len(new_ranges) == 1:
            return TextPositionSelector.from_range(new_ranges[0])

        return TextPositionSet.from_ranges(new_rangeset)

    @classmethod
    def from_text(
        cls,
        text: str,
        start: Union[int, str] = 0,
        end: Optional[Union[int, str]] = None,
    ) -> TextPositionSelector:
        if isinstance(start, str):
            start_index = text.find(start)
            if start_index == -1:
                raise TextSelectionError(f"String {start} not found in text.")
            start = start_index

        if isinstance(end, str):
            end_index = text.find(end)
            if end_index == -1:
                raise TextSelectionError(f"String {end} not found in text.")
            end = end_index + len(end)

        return cls(start=start, end=end)

    def __sub__(
        self, value: Union[int, TextPositionSelector, TextPositionSet]
    ) -> TextPositionSelector:
        if not isinstance(value, int):
            return self.difference(value)
        new_start = max(0, self.start - value)

        if self.end is None:
            new_end = self.end
        else:
            new_end = self.end - value
            if new_end < 0:
                raise IndexError(
                    f"Subtracting {value} from ({self.start}, {self.end}) "
                    "would result in a negative end position."
                )

        return TextPositionSelector(
            start=new_start,
            end=new_end,
        )

    def difference(
        self, rng: Union[TextPositionSet, TextPositionSelector]
    ) -> Union[TextPositionSet, TextPositionSelector]:
        """
        Apply Range difference method replacing RangeSet with TextPositionSet in return value.
        """
        if isinstance(rng, TextPositionSet):
            to_compare: Union[Range, RangeSet] = rng.rangeset()
        elif isinstance(rng, TextPositionSelector):
            to_compare = rng.range()
        else:
            to_compare = rng
        new_rangeset = self.rangeset().difference(to_compare)
        if len(new_rangeset.ranges()) == 1:
            return TextPositionSelector.from_range(new_rangeset.ranges()[0])
        return TextPositionSet.from_ranges(new_rangeset)

    def as_quote_selector(
        self, text: str, left_margin: int = 0, right_margin: int = 0
    ) -> TextQuoteSelector:
        """
        Make a quote selector, creating prefix and suffix from specified lengths of text.

        :param text:
            the passage where an exact quotation needs to be located

        :param left_margin:
            number of characters to look backward to create :attr:`TextQuoteSelector.prefix`

        :param right_margin:
            number of characters to look forward to create :attr:`TextQuoteSelector.suffix`
        """
        if self.start >= len(text):
            raise IndexError(
                f"String of length {len(text)} is not long enough "
                f"to include any of the range ({self.start}, {self.end})"
            )

        if isinstance(self.end, int):
            end = self.end
        else:
            end = len(text)

        exact = text[self.start : end]

        prefix = text[max(0, self.start - left_margin) : self.start]
        suffix = text[end : min(len(text), end + right_margin)]

        new_selector = TextQuoteSelector(exact=exact, prefix=prefix, suffix=suffix)
        return new_selector

    def unique_quote_selector(self, text: str) -> TextQuoteSelector:
        """
        Add text to prefix and suffix as needed to make selector unique in the source text.

        :param text:
            the passage where an exact quotation needs to be located
        """
        exact = text[self.start : self.end]
        margins = 0
        while margins < (len(text) - len(exact)):
            new_selector = self.as_quote_selector(
                text=text, left_margin=margins, right_margin=margins
            )
            if new_selector.is_unique_in(text):
                return new_selector
            margins += 5
        return TextQuoteSelector(
            exact=exact, prefix=text[: self.start], suffix=text[self.end :]
        )

    def combine(self, other: TextPositionSelector, text: str):
        """Make new selector combining ranges of self and other if it will fit in text."""
        for selector in (self, other):
            selector.verify_text_positions(text)
        return self + other

    def dump(self):
        """Serialize the selector."""
        return {"type": "TextPositionSelector", "start": self.start, "end": self.end}

    def passage(self, text: str) -> str:
        """Get the quotation from text identified by start and end positions."""
        self.verify_text_positions(text)
        return text[self.start : self.end]

    def verify_text_positions(self, text: str) -> None:
        """Verify that selector's text positions exist in text."""
        if self.end and self.end > len(text):
            raise IndexError(
                f'Text "{text}" is too short to include '
                + f"the interval ({self.start}, {self.end})"
            )
        return None


class TextPositionSet(BaseModel):
    r"""
    A set of TextPositionSelectors.
    """

    selectors: List[TextPositionSelector] = []

    @classmethod
    def from_ranges(
        cls, ranges: Union[RangeSet, Range, List[Range]]
    ) -> TextPositionSet:
        if isinstance(ranges, RangeSet):
            ranges = ranges.ranges()
        if isinstance(ranges, Range):
            ranges = [ranges]
        selectors = [TextPositionSelector.from_range(item) for item in ranges]
        return cls(selectors=selectors)

    def __str__(self):
        return repr(self)

    def __add__(
        self, value: Union[int, TextPositionSelector, TextPositionSet]
    ) -> TextPositionSet:
        """
        Increase all startpoints and endpoints by the given amount.

        :param value:
            selector for another text interval, or integet to add to every
            start and end value in self's position selectors

        :returns:
            a selector reflecting the combined range if possible, otherwise None
        """
        if not isinstance(value, int):
            return self | value
        return TextPositionSet(
            selectors=[text_range + value for text_range in self.selectors]
        )

    def merge_rangeset(self, rangeset: RangeSet) -> "TextPositionSet":
        """
        Merge another RangeSet into this one, returning a new TextPositionSet.

        :param rangeset:
            the RangeSet to merge

        :returns:
            a new TextPositionSet representing the combined ranges
        """
        new_rangeset = self.rangeset() | rangeset
        return TextPositionSet.from_ranges(new_rangeset)

    def __gt__(
        self, other: Union[TextPositionSelector, TextPositionSet, Range, RangeSet]
    ) -> bool:
        if isinstance(other, TextPositionSet):
            to_compare: Union[Range, RangeSet] = other.rangeset()
        elif isinstance(other, TextPositionSelector):
            to_compare = other.range()
        else:
            to_compare = other
        return not bool(to_compare.difference(self.rangeset()))

    def __ge__(
        self, other: Union[TextPositionSelector, TextPositionSet, Range, RangeSet]
    ) -> bool:
        if self == other:
            return True
        return self > other

    def __or__(
        self, other: Union[TextPositionSet, TextPositionSelector]
    ) -> TextPositionSet:
        if isinstance(other, TextPositionSelector):
            other = TextPositionSet(selectors=[other])
        return self.merge_rangeset(other.rangeset())

    def __and__(
        self, other: Union[TextPositionSet, TextPositionSelector]
    ) -> TextPositionSet:
        if isinstance(other, TextPositionSelector):
            other = TextPositionSet(selectors=[other])
        new_rangeset = self.rangeset() & other.rangeset()
        return TextPositionSet.from_ranges(new_rangeset)

    def __sub__(
        self, value: Union[int, TextPositionSelector, TextPositionSet]
    ) -> TextPositionSet:
        """Decrease all startpoints and endpoints by the given amount."""
        if not isinstance(value, int):
            new_rangeset = self.rangeset() - value.rangeset()
            return TextPositionSet.from_ranges(new_rangeset)
        ranges = [selector - value for selector in self.selectors]
        return TextPositionSet.from_ranges(ranges)

    @validator("selectors", pre=True)
    def selectors_are_in_list(
        cls, selectors: Union[TextPositionSelector, List[TextPositionSelector]]
    ):
        """Put single selector in list."""
        if isinstance(selectors, TextPositionSelector):
            selectors = [selectors]
        return selectors

    @validator("selectors")
    def order_of_selectors(cls, v):
        """Ensure that selectors are in order."""
        return sorted(v, key=lambda x: x.start)

    def as_quotes(self, text: str) -> List[TextQuoteSelector]:
        return [selector.unique_quote_selector(text) for selector in self.selectors]

    def as_text_sequence(self, text: str, include_nones: bool = True) -> TextSequence:
        """
        List the phrases in the Enactment selected by TextPositionSelectors.

        :param passage:
            A passage to select text from

        :param include_nones:
            Whether the list of phrases should include `None` to indicate a block of
            unselected text
        """
        selected: List[Union[None, TextPassage]] = []

        selection_ranges = self.ranges()

        if selection_ranges:
            if include_nones and 0 < selection_ranges[0].start < len(text):
                selected.append(None)
            for passage in selection_ranges:
                if passage.start < passage.end and passage.start < len(text):
                    selected.append(TextPassage(text[passage.start : passage.end]))
                if include_nones and passage.end and (passage.end < len(text)):
                    selected.append(None)
        elif text and include_nones and (not selected or selected[-1] is not None):
            selected.append(None)
        return TextSequence(selected)

    def rangeset(self) -> RangeSet:
        ranges = [selector.range() for selector in self.selectors]
        return RangeSet(ranges)

    def ranges(self) -> List[Range]:
        return self.rangeset().ranges()

    def as_string(self, text: str) -> str:
        """Return a string representing the selected parts of `text`."""
        text_sequence = self.as_text_sequence(text)
        return str(text_sequence)

    def add_margin(
        self,
        text: str,
        margin_width: int = 3,
        margin_characters: str = """,."' ;[]()""",
    ) -> TextPositionSet:
        if margin_width < 1:
            raise ValueError("margin_width must be a positive integer")
        margin_selectors = TextPositionSet()
        for left in self.ranges():
            for right in self.ranges():
                if left.end < right.start <= left.end + margin_width:
                    if all(
                        letter in margin_characters
                        for letter in text[left.end : right.start]
                    ):
                        margin_selectors += TextPositionSelector(
                            start=left.end, end=right.start
                        )
        return self + margin_selectors
