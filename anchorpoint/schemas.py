"""Schema for serializing text selectors."""

from typing import Dict, Mapping, Optional, Sequence, TypedDict, Union

from marshmallow import Schema, fields, pre_dump, post_load, pre_load

from anchorpoint.textselectors import (
    TextQuoteSelector,
    TextPositionSelector,
    TextPositionSet,
)


class PositionSelectorDict(TypedDict, total=False):
    """Dict representing TextPositionSelector, to be loaded with SelectorSchema."""

    start: int
    end: Optional[int]
    include_start: bool
    include_end: bool


class SelectorSchema(Schema):
    r"""
    Schema for loading a :class:`~anchorpoint.textselectors.TextQuoteSelector` or
    :class:`~anchorpoint.textselectors.TextPositionSelector`.

    Generates a :class:`~anchorpoint.textselectors.TextQuoteSelector`
    if the input data contains any of the fields "exact", "prefix",
    or "suffix", and returns a
    :class:`~anchorpoint.textselectors.TextPositionSelector` otherwise.

    """
    __model__ = TextQuoteSelector

    exact = fields.Str(missing=None)
    prefix = fields.Str(missing=None)
    suffix = fields.Str(missing=None)

    start = fields.Int()
    end = fields.Int(missing=None)
    include_start = fields.Bool(missing=True, load_only=True)
    include_end = fields.Bool(missing=False, load_only=True)

    class Meta:
        ordered = True

    @pre_dump
    def get_real_start_and_end(self, obj, many=False):
        if isinstance(obj, TextPositionSelector):
            obj.start = obj.real_start
            obj.end = obj.real_end
        return obj

    def expand_anchor_shorthand(self, text: str) -> Mapping[str, str]:
        """
        Convert input from shorthand format to normal selector format.

        .. code-block:: python

            >>> schema = SelectorSchema()
            >>> schema.expand_anchor_shorthand("eats,|shoots,|and leaves")
            {'exact': 'shoots,', 'prefix': 'eats,', 'suffix': 'and leaves'}
        """
        result = {}
        (
            result["prefix"],
            result["exact"],
            result["suffix"],
        ) = TextQuoteSelector.split_anchor_text(text)
        return result

    def convert_bool_to_dict(self, data: bool) -> Dict[str, int]:
        """Interpret True as a TextPositionSelector including the whole section."""

        if data is True:
            return {"start": 0}
        return {"start": 0, "end": 0}

    @pre_load
    def preprocess_data(
        self, data: Union[str, bool, Mapping[str, Union[str, bool, int]]], **kwargs
    ) -> Mapping[str, Union[str, bool, int]]:
        if isinstance(data, bool):
            return self.convert_bool_to_dict(data)
        if isinstance(data, str):
            return self.expand_anchor_shorthand(data)
        if "text" in data.keys() and isinstance(data["text"], str):
            return self.expand_anchor_shorthand(data["text"])
        return data

    @post_load
    def make_object(
        self, data, **kwargs
    ) -> Optional[Union[TextPositionSelector, TextQuoteSelector]]:
        if data.get("exact") or data.get("prefix") or data.get("suffix"):
            for unwanted in ("start", "end", "include_start", "include_end"):
                data.pop(unwanted, None)
            return TextQuoteSelector(**data)

        if data.get("start") == data.get("end"):
            return None

        for unwanted in ("exact", "prefix", "suffix"):
            data.pop(unwanted, None)
        return TextPositionSelector(**data)


class TextPositionSetFactory:
    r"""Factory for constructing :class:`~anchorpoint.textselectors.TextPositionSet` from text passages and various kinds of selector."""

    def __init__(self, passage: str) -> None:
        self.passage = passage

    def from_bool(self, selection: bool) -> TextPositionSet:
        if selection is True:
            return TextPositionSet(TextPositionSelector(0, len(self.passage)))
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
            schema = SelectorSchema()
            data = schema.expand_anchor_shorthand(selection)
            selection = schema.load(data)
        if isinstance(selection, TextQuoteSelector):
            selection = [selection]
        elif isinstance(selection, TextPositionSelector):
            return TextPositionSet(selection)
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
        positions = []
        for selection in selections:
            if isinstance(selection, str):
                selection = TextQuoteSelector(exact=selection)
            if isinstance(selection, TextQuoteSelector):
                selection = selection.as_position(self.passage)
            positions.append(selection)
        return TextPositionSet(positions)

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
        position_selectors = [quote.as_position(self.passage) for quote in quotes]
        return TextPositionSet(position_selectors)
