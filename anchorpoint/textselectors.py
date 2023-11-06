"""
Text substring selectors for anchoring annotations.

Based on parts of the W3C `Web Annotation Data
Model <https://www.w3.org/TR/annotation-model/>`_.
"""

from __future__ import annotations

import re

from typing import List, Optional, Sequence, Tuple, TypeVar, Union
from anchorpoint.textsequences import TextPassage, TextSequence
from ranges import Range, RangeSet, Inf
from ranges._helper import _InfiniteValue
from pydantic import BaseModel, field_validator, model_validator


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

    @field_validator("prefix", "exact", "suffix", mode="before")
    @classmethod
    def no_none_for_prefix(cls, value: str | None) -> str:
        """Ensure that 'prefix', 'exact', and 'suffix' are not None."""
        if value is None:
            return ""
        return value

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

    def as_unique_position(self, text: str) -> TextPositionSelector:
        """
        Get the interval where the selected quote appears in "text".

        :param text:
            the passage where an exact quotation needs to be located

        :returns:
            the position selector for the location of the exact quotation
        """
        position = self.as_position(text)

        if not self.is_unique_in(text):
            raise TextSelectionError(
                f"Text selection {self} cannot be positioned because it "
                f"is not unique in the given text."
            )
        return position

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


ST = TypeVar("ST")


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
    def from_range(
        cls, range: Union[Range, TextPositionSelector]
    ) -> TextPositionSelector:
        """Make TextPositionSelector with same extent as a Range object from python-ranges."""
        if isinstance(range.end, _InfiniteValue):
            end = None
        else:
            end = range.end
        return TextPositionSelector(start=range.start, end=end)

    @field_validator("start", mode="after")
    @classmethod
    def start_not_negative(cls, v: int) -> int:
        """
        Verify start position is not negative.

        :returns:
            the start position, which is not negative
        """
        if v < 0:
            raise IndexError("Start position for text range cannot be negative.")
        return v

    @model_validator(mode="after")
    def start_less_than_end(self) -> "TextPositionSelector":
        """
        Verify start position is before the end position.

        :returns:
            the end position, which after the start position
        """
        if self.end is not None and self.end <= self.start:
            raise IndexError("End position must be greater than start position.")
        return self

    def range(self) -> Range:
        """Get the range of the text."""
        return Range(start=self.start, end=self.end or Inf)

    def rangeset(self) -> RangeSet:
        """Get the range set of the text."""
        return RangeSet([self.range()])

    def __add__(
        self, value: Union[int, TextPositionSelector]
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

    def __gt__(self, other: Union[TextPositionSelector, TextPositionSet]) -> bool:
        """
        Check if self is greater than other.

        :param other:
            selector for another text interval

        :returns:
            whether self is greater than other
        """
        return self >= other and self != other

    def __ge__(self, other: Union[TextPositionSelector, TextPositionSet]) -> bool:
        return self.rangeset() | other.rangeset() == self.rangeset()

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

    def __and__(
        self, other: Union[TextPositionSelector, TextPositionSet, Range, RangeSet]
    ) -> Optional[TextPositionSelector]:
        """
        Make a new selector covering the intersection of the ranges of self and other.

        :param other:
            selector for another text interval

        :returns:
            a selector reflecting the range of the intersection
        """
        if isinstance(other, (TextPositionSelector, TextPositionSet)):
            other = other.rangeset()

        new_rangeset: RangeSet = self.rangeset() & other

        if not new_rangeset:
            return None
        return TextPositionSelector.from_range(new_rangeset.ranges()[0])

    @classmethod
    def from_text(
        cls,
        text: str,
        start: Union[int, str] = 0,
        end: Optional[Union[int, str]] = None,
    ) -> TextPositionSelector:
        """Make position selector including the text strings "start" and "end" within "text"."""
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

    def subtract_integer(self, value: int) -> TextPositionSelector:
        """Reduce self's startpoint and endpoint by an integer."""
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

    def __sub__(
        self, value: Union[int, TextPositionSelector, TextPositionSet]
    ) -> Union[TextPositionSelector, TextPositionSet]:
        if not isinstance(value, int):
            return self.difference(value)
        return self.subtract_integer(value)

    def difference(
        self, other: Union[TextPositionSet, TextPositionSelector]
    ) -> Union[TextPositionSet, TextPositionSelector]:
        """
        Get selectors in self or other but not both.

        Applies Range difference, method replacing RangeSet
        with :class:`.TextPositionSet` in return value.
        """
        if isinstance(other, TextPositionSet):
            to_compare: Union[Range, RangeSet] = other.rangeset()
        elif isinstance(other, TextPositionSelector):
            to_compare = other.range()
        else:
            to_compare = other
        new_rangeset = self.rangeset().difference(to_compare)
        if len(new_rangeset.ranges()) == 1:
            return TextPositionSelector.from_range(new_rangeset.ranges()[0])
        return TextPositionSet.from_ranges(new_rangeset)

    def as_quote(
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

        return TextQuoteSelector(exact=exact, prefix=prefix, suffix=suffix)

    def unique_quote_selector(self, text: str) -> TextQuoteSelector:
        """
        Add text to prefix and suffix as needed to make selector unique in the source text.

        :param text:
            the passage where an exact quotation needs to be located
        """
        exact = text[self.start : self.end]
        for margins in range(0, len(text) - len(exact), 5):
            new_selector = self.as_quote(
                text=text, left_margin=margins, right_margin=margins
            )
            if new_selector.is_unique_in(text):
                return new_selector
        return TextQuoteSelector(
            exact=exact, prefix=text[: self.start], suffix=text[self.end :]
        )

    def combine(self, other: TextPositionSelector, text: str):
        """Make new selector combining ranges of self and other if it will fit in text."""
        for selector in (self, other):
            selector.verify_text_positions(text)
        return self + other

    def select_text(self, text: str) -> str:
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
    r"""A set of TextPositionSelectors."""

    positions: List[TextPositionSelector] = []
    quotes: List[TextQuoteSelector] = []

    @classmethod
    def from_quotes(
        cls,
        selection: Union[str, TextQuoteSelector, List[Union[TextQuoteSelector, str]]],
    ) -> TextPositionSet:
        """
        Construct TextPositionSet from string or TextQuoteSelectors.

        If a string is used, it will be converted to a :class:`.TextQuoteSelector` with no prefix or suffix.
        """
        if isinstance(selection, (str, TextQuoteSelector)):
            selection = [selection]
        selection_as_selectors: list[TextQuoteSelector] = [
            TextQuoteSelector.from_text(s) if isinstance(s, str) else s
            for s in selection
        ]
        return TextPositionSet(quotes=selection_as_selectors)

    @classmethod
    def from_ranges(
        cls, ranges: Union[RangeSet, Range, List[Range], List[TextPositionSelector]]
    ) -> TextPositionSet:
        """Make new class instance from Range objects from python-ranges library."""
        if isinstance(ranges, RangeSet):
            ranges = ranges.ranges()
        if isinstance(ranges, Range):
            ranges = [ranges]
        selectors = [TextPositionSelector.from_range(item) for item in ranges]
        return cls(positions=selectors)

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
            positions=[text_range + value for text_range in self.positions],
            quotes=self.quotes,
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
        result = TextPositionSet.from_ranges(new_rangeset)
        result.quotes = self.quotes
        return result

    def __gt__(
        self, other: Union[TextPositionSelector, TextPositionSet, Range, RangeSet]
    ) -> bool:
        """Test if self's rangeset includes all of other's rangeset, but is not identical."""
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
        """Test if self's rangeset includes all of other's rangeset."""
        if self == other:
            return True
        return self > other

    def __or__(
        self, other: Union[TextPositionSet, TextPositionSelector]
    ) -> TextPositionSet:
        if isinstance(other, TextPositionSelector):
            other = TextPositionSet(positions=[other])
        return self.merge_rangeset(other.rangeset())

    def __and__(
        self, other: Union[TextPositionSet, TextPositionSelector]
    ) -> TextPositionSet:
        if isinstance(other, TextPositionSelector):
            other = TextPositionSet(positions=[other])
        new_rangeset: RangeSet = self.rangeset() & other.rangeset()
        return TextPositionSet.from_ranges(new_rangeset)

    def __sub__(
        self, value: Union[int, TextPositionSelector, TextPositionSet]
    ) -> TextPositionSet:
        """Decrease all startpoints and endpoints by the given amount."""
        if not isinstance(value, int):
            new_rangeset = self.rangeset() - value.rangeset()
            new = TextPositionSet.from_ranges(new_rangeset)
        else:
            new_selectors = [
                selector.subtract_integer(value) for selector in self.positions
            ]
            new = TextPositionSet.from_ranges(new_selectors)
        new.quotes = self.quotes
        return new

    @field_validator("quotes", mode="before")
    def quote_selectors_are_in_list(
        cls,
        selectors: Union[str, TextQuoteSelector, List[Union[str, TextQuoteSelector]]],
    ):
        """Put single selector in list and convert strings to selectors."""
        if isinstance(selectors, str) or not isinstance(selectors, Sequence):
            selectors = [selectors]

        selectors = [
            TextQuoteSelector.from_text(selector)
            if isinstance(selector, str)
            else selector
            for selector in selectors
        ]
        return selectors

    @field_validator("positions", mode="before")
    @classmethod
    def is_sequence(cls, v: ST | Sequence[ST]) -> Sequence[ST]:
        """Ensure that selectors are in a sequence."""
        if not isinstance(v, Sequence):
            v = [v]
        return v

    @field_validator("positions", mode="after")
    @classmethod
    def order_of_selectors(cls, v: list[TextPositionSelector]):
        """Ensure that selectors are in order."""
        return sorted(v, key=lambda x: x.start)

    def positions_as_quotes(self, text: str) -> List[TextQuoteSelector]:
        """Copy self's position selectors, converted to quote selectors."""
        return [selector.unique_quote_selector(text) for selector in self.positions]

    def as_quotes(self, text: str) -> List[TextQuoteSelector]:
        """Copy self's quote and position selectors, converting all position selectors to quote selectors."""
        return self.positions_as_quotes(text) + self.quotes

    def convert_quotes_to_positions(self, text: str) -> "TextPositionSet":
        """Return new TextPositionSet with all quotes replaced by their positions in the given text."""
        return self.merge_rangeset(self.quotes_rangeset(text))

    def as_text_sequence(self, text: str, include_nones: bool = True) -> TextSequence:
        """
        List the phrases in a text passage selected by this TextPositionSet.

        :param passage:
            A passage to select text from

        :param include_nones:
            Whether the list of phrases should include `None` to indicate a block of
            unselected text

        :returns:
            A TextSequence of the phrases in the text

        >>> selectors = [TextPositionSelector(start=5, end=10)]
        >>> selector_set = TextPositionSet(positions=selectors)
        >>> selector_set.as_text_sequence("Some text.")
        TextSequence([None, TextPassage("text.")])
        """
        selected: List[Union[None, TextPassage]] = []

        position_ranges = self.rangeset()
        quote_ranges = self.quotes_rangeset(text=text)

        selection_rangeset = position_ranges | quote_ranges
        selection_ranges = selection_rangeset.ranges()

        if selection_ranges:
            if include_nones and 0 < selection_ranges[0].start < len(text):
                selected.append(None)
            for passage in selection_ranges:
                if (
                    passage.start is not None
                    and passage.start < passage.end
                    and passage.start < len(text)
                ):
                    string_end = (
                        passage.end
                        if not isinstance(passage.end, _InfiniteValue)
                        else None
                    )
                    selected.append(TextPassage(text[passage.start : string_end]))
                if include_nones and passage.end and (passage.end < len(text)):
                    selected.append(None)
        elif text and include_nones and (not selected or selected[-1] is not None):
            selected.append(None)
        return TextSequence(selected)

    def rangeset(self) -> RangeSet:
        """Convert positions into python-ranges Rangeset."""
        ranges = [selector.range() for selector in self.positions]
        return RangeSet(ranges)

    def positions_of_quote_selectors(self, text: str) -> List[TextPositionSelector]:
        """Convert self's quote selectors to position selectors for a given text."""
        return [selector.as_position(text) for selector in self.quotes]

    def quotes_rangeset(self, text: str) -> RangeSet:
        """Get ranges where these quotes appear in the provided text."""
        return RangeSet(
            [selector.range() for selector in self.positions_of_quote_selectors(text)]
        )

    def ranges(self) -> List[Range]:
        """Get positions as Range objects from python-ranges library."""
        return self.rangeset().ranges()

    def as_string(self, text: str) -> str:
        """
        Return a string representing the selected parts of `text`.

        >>> selectors = [TextPositionSelector(start=5, end=10)]
        >>> selector_set = TextPositionSet(positions=selectors)
        >>> sequence = selector_set.as_text_sequence("Some text.")
        >>> selector_set.as_string("Some text.")
        '…text.'
        """
        text_sequence = self.as_text_sequence(text)
        return str(text_sequence)

    def add_margin(
        self,
        text: str,
        margin_width: int = 3,
        margin_characters: str = """,."' ;[]()""",
    ) -> TextPositionSet:
        """
        Expand selected position selectors to include margin of punctuation.

        This can cause multiple selections to be merged into a single one.

        Ignores quote selectors.

        :param text:
            The text that passages are selected from

        :param margin_width:
            The width of the margin to add

        :param margin_characters:
            The characters to include in the margin

        :returns:
            A new TextPositionSet with the margin added

        >>> from anchorpoint.textselectors import TextPositionSetFactory
        >>> text = "I predict that the grass is wet. (It rained.)"
        >>> factory = TextPositionSetFactory(text=text)
        >>> selectors = [TextQuoteSelector(exact="the grass is wet"), TextQuoteSelector(exact="it rained")]
        >>> position_set = factory.from_selection(selection=selectors)
        >>> len(position_set.ranges())
        2
        >>> new_position_set = position_set.add_margin(text=text)
        >>> len(new_position_set.ranges())
        1
        >>> new_position_set.ranges()[0].start
        15
        >>> new_position_set.ranges()[0].end
        43

        """
        if margin_width < 1:
            raise ValueError("margin_width must be a positive integer")

        new_rangeset = self.rangeset() | self.quotes_rangeset(text)
        margin_selectors = TextPositionSet()
        for left in new_rangeset.ranges():
            for right in new_rangeset.ranges():
                if (
                    left.end is not None
                    and left.end < right.start <= left.end + margin_width
                ):
                    if all(
                        letter in margin_characters
                        for letter in text[left.end : right.start]
                    ):
                        margin_selectors += TextPositionSelector(
                            start=left.end, end=right.start
                        )
        with_margin = new_rangeset + margin_selectors.rangeset()
        return TextPositionSet.from_ranges(with_margin)

    def select_text(
        self,
        text: str,
        margin_width: int = 3,
        margin_characters: str = """,."' ;[]()""",
    ) -> str:
        """
        Return the selected text from `text`.

        :param text:
            The text that passages are selected from

        :param margin_width:
            The width of the margin to add

        :param margin_characters:
            The characters to include in the margin

        :returns:
            The selected text

        >>> from anchorpoint.textselectors import TextPositionSetFactory
        >>> text = "I predict that the grass is wet. (It rained.)"
        >>> factory = TextPositionSetFactory(text=text)
        >>> selectors = [TextQuoteSelector(exact="the grass is wet"), TextQuoteSelector(exact="it rained")]
        >>> position_set = factory.from_selection(selection=selectors)
        >>> position_set.select_text(text=text)
        '…the grass is wet. (It rained…'
        """
        with_margin = self.add_margin(
            text=text, margin_width=margin_width, margin_characters=margin_characters
        )
        text_sequence = with_margin.as_text_sequence(text)
        return str(text_sequence)


class TextPositionSetFactory:
    r"""Factory for constructing :class:`~anchorpoint.textselectors.TextPositionSet` from text passages and various kinds of selector."""

    def __init__(self, text: str) -> None:
        """Store text passage that will be used to generate text selections."""
        self.text = text

    def from_bool(self, selection: bool) -> TextPositionSet:
        """Select either the whole passage or none of it."""
        if selection is True:
            return TextPositionSet(
                positions=[TextPositionSelector(start=0, end=len(self.text))]
            )
        return TextPositionSet()

    def from_selection(
        self,
        selection: Union[
            bool,
            str,
            TextPositionSelector,
            TextQuoteSelector,
            Sequence[Union[str, TextQuoteSelector, TextPositionSelector]],
        ],
    ) -> TextPositionSet:
        """Construct TextPositionSet for a provided text passage, from any type of selector."""
        if isinstance(selection, str):
            selection = TextQuoteSelector.from_text(selection)
        if isinstance(selection, TextQuoteSelector):
            selection = [selection]
        elif isinstance(selection, TextPositionSelector):
            return TextPositionSet(positions=[selection])
        if isinstance(selection, bool):
            return self.from_bool(selection)
        return self.from_selection_sequence(selection)

    def from_selection_sequence(
        self, selections: Sequence[Union[str, TextQuoteSelector, TextPositionSelector]]
    ) -> TextPositionSet:
        """
        Construct TextPositionSet from one or more of: strings, Quote Selectors, and Position Selectors.

        First converts strings to TextQuoteSelectors, and then to TextPositionSelectors.
        """
        if isinstance(selections, TextPositionSet):
            return selections
        positions = []
        for selection in selections:
            if isinstance(selection, str):
                selection = TextQuoteSelector(exact=selection)
            if isinstance(selection, TextQuoteSelector):
                selection = selection.as_position(self.text)
            elif not isinstance(selection, TextPositionSelector):
                selection = TextPositionSelector(start=selection[0], end=selection[1])
            positions.append(selection)
        return TextPositionSet(positions=positions)

    def from_exact_strings(self, selection: Sequence[str]) -> TextPositionSet:
        """
        Construct TextPositionSet from a sequence of strings representing exact quotations.

        First converts the sequence to TextQuoteSelectors, and then to TextPositionSelectors.
        """
        selectors = [TextQuoteSelector(exact=item) for item in selection]
        return self.from_quote_selectors(quotes=selectors)

    def from_quote_selectors(
        self, quotes: Sequence[TextQuoteSelector]
    ) -> TextPositionSet:
        """Construct TextPositionSet from a sequence of TextQuoteSelectors."""
        position_selectors = [quote.as_position(self.text) for quote in quotes]
        return TextPositionSet(positions=position_selectors)
