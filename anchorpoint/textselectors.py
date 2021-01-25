"""
Text substring selectors for anchoring annotations.

Based on parts of the W3C `Web Annotation Data
Model <https://www.w3.org/TR/annotation-model/>`_.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from typing import List, Optional, Tuple, Union

from anchorpoint.textsequences import TextPassage, TextSequence
from anchorpoint.utils._helper import _is_iterable_non_string
from anchorpoint.utils.ranges import Range, RangeSet
from marshmallow import ValidationError


class TextSelectionError(Exception):
    """Exception for failing to select text as described by user."""

    pass


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
        raise ValidationError(
            "If the 'text' field includes | pipe separators, it must contain exactly "
            "two, separating the string into 'prefix', 'exact', and 'suffix'."
        )

    @classmethod
    def from_text(cls, text: str) -> TextQuoteSelector:
        split_text = cls.split_anchor_text(text)
        return cls(prefix=split_text[0], exact=split_text[1], suffix=split_text[2])

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
            return TextPositionSelector(match.start(1), match.end(1))
        raise TextSelectionError(
            f'Unable to find pattern "{self.passage_regex()}" in text: "{text}"'
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.start < 0:
            raise IndexError("Start position for text range cannot be negative.")
        if self.end is not None and self.start >= self.end:
            raise IndexError("Selected end position must be after the start position.")

    def __repr__(self):
        return super().__repr__().replace("Range", "TextPositionSelector")

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

        if str(self.end) == "inf":
            new_end = self.end
        else:
            new_end = self.end + value

        return TextPositionSelector(
            start=self.start + value,
            end=new_end,
            include_start=self.include_start,
            include_end=self.include_end,
        )

    @property
    def real_start(self) -> int:
        """Start value following Python convention of including first character."""
        if not self.include_start:
            return self.start + 1
        return self.start

    @property
    def real_end(self) -> int:
        """Start value following Python convention of excluding first character."""
        if self.include_end:
            return self.end + 1
        return self.end

    def __sub__(self, value: Union[int, TextPositionSelector]) -> TextPositionSelector:
        if not isinstance(value, int):
            return super().__sub__(value)
        new_start = max(0, self.start - value)

        if str(self.end) == "inf":
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
            include_start=self.include_start,
            include_end=self.include_end,
        )

    def difference(
        self, rng: Union[TextPositionSet, TextPositionSelector]
    ) -> Union[TextPositionSet, TextPositionSelector]:
        """
        Apply Range difference method replacing RangeSet with TextPositionSet in return value.
        """
        result = super().difference(rng)
        if isinstance(result, RangeSet):
            result = TextPositionSet(result)
        return result

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
    def __init__(self, *args):
        """
        Constructs a new TextPositionSet containing the given sub-ranges.
        """
        # flatten args
        temp_list = []
        for arg in args:
            if isinstance(arg, TextPositionSelector):
                temp_list.append(arg)
            elif _is_iterable_non_string(arg):
                temp_list.extend(TextPositionSelector(x) for x in arg)
            else:
                temp_list.append(TextPositionSelector(arg))
        # assign own Ranges
        self._ranges = self.__class__._merge_ranges(temp_list)

    def __repr__(self):
        return super().__repr__().replace("RangeSet", self.__class__.__name__)

    def __str__(self):
        return f"TextPositionSet({self.ranges()})"

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
        return TextPositionSet([text_range + value for text_range in self])

    def __sub__(
        self, value: Union[int, TextPositionSelector, TextPositionSet]
    ) -> TextPositionSet:
        """Decrease all startpoints and endpoints by the given amount."""
        if not isinstance(value, int):
            return super().__sub__(value)
        return TextPositionSet([text_range - value for text_range in self])

    def as_quotes(self, text: str) -> List[TextQuoteSelector]:
        quotes = [selector.unique_quote_selector(text) for selector in self.ranges()]
        return quotes

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
                end_value = (
                    None
                    if passage.end > 999999
                    else passage.end + int(passage.include_end)
                )
                if passage.start < end_value and passage.start < len(text):
                    selected.append(TextPassage(text[passage.start : end_value]))
                if include_nones and end_value and (end_value < len(text)):
                    selected.append(None)
        elif text and include_nones and (not selected or selected[-1] is not None):
            selected.append(None)
        return TextSequence(selected)

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
                if left.real_end < right.real_start <= left.real_end + margin_width:
                    if all(
                        letter in margin_characters
                        for letter in text[left.real_end : right.real_start]
                    ):
                        margin_selectors += TextPositionSelector(
                            start=left.real_end, end=right.real_start
                        )
        return self + margin_selectors
