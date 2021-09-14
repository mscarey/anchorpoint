"""Schema for serializing text selectors."""

from typing import Dict, List, Mapping, Optional, Sequence, TypedDict, Union

from marshmallow import Schema, fields, post_load, pre_load

from anchorpoint.textselectors import (
    TextQuoteSelector,
    TextPositionSelector,
    TextPositionSet,
)


class PositionSelectorDict(TypedDict, total=False):
    """Dict representing TextPositionSelector, to be loaded with SelectorSchema."""

    start: int
    end: Optional[int]


class PositionSchema(Schema):
    r"""Schema for :class:`~anchorpoint.textselectors.TextPositionSelector`."""
    __model__ = TextPositionSelector

    start = fields.Int()
    end = fields.Int(load_default=None)

    class Meta:
        ordered = True

    def convert_bool_to_dict(self, data: bool) -> Dict[str, int]:
        """Interpret True as a TextPositionSelector including the whole section."""

        if data is True:
            return {"start": 0}
        return {"start": 0, "end": 0}

    @pre_load
    def preprocess_data(
        self, data: Union[bool, Mapping[str, int]], **kwargs
    ) -> Mapping[str, int]:
        if isinstance(data, bool):
            return self.convert_bool_to_dict(data)
        return data

    @post_load
    def make_object(
        self, data: PositionSelectorDict, **kwargs
    ) -> Optional[TextPositionSelector]:
        if data["start"] == data.get("end") == 0:
            return None
        return TextPositionSelector(**data)


class QuoteSchema(Schema):
    r"""Schema for :class:`~anchorpoint.textselectors.TextPositionSelector`."""
    __model__ = TextQuoteSelector

    prefix = fields.Str(load_default=None)
    exact = fields.Str(load_default=None)
    suffix = fields.Str(load_default=None)

    class Meta:
        ordered = True

    def expand_anchor_shorthand(self, text: str) -> Mapping[str, str]:
        """
        Convert input from shorthand format to normal selector format.

            >>> schema = SelectorSchema()
            >>> schema.expand_anchor_shorthand("eats,|shoots,|and leaves")
            {'prefix': 'eats,', 'exact': 'shoots,', 'suffix': 'and leaves'}
        """
        result = {}
        (
            result["prefix"],
            result["exact"],
            result["suffix"],
        ) = TextQuoteSelector.split_anchor_text(text)
        return result

    @pre_load
    def preprocess_data(
        self, data: Union[str, Mapping[str, str]], **kwargs
    ) -> Mapping[str, str]:
        if isinstance(data, str):
            return self.expand_anchor_shorthand(data)
        return data

    @post_load
    def make_object(self, data: Dict[str, str], **kwargs) -> TextQuoteSelector:

        return TextQuoteSelector(**data)


class TextPositionSetSchema(Schema):
    """Schema for a set of positions in a text."""

    __model__ = TextPositionSet
    quotes = fields.Nested(QuoteSchema, many=True)
    positions = fields.Nested(PositionSchema, many=True)

    @pre_load
    def preprocess_data(
        self,
        data: Union[
            str, Mapping[str, Union[Mapping[str, str], List[Mapping[str, str]]]]
        ],
        **kwargs
    ) -> Mapping[str, List[Mapping[str, str]]]:
        if isinstance(data.get("quotes"), dict):
            data["quotes"] = [data["quotes"]]
        if isinstance(data.get("positions"), dict):
            data["positions"] = [data["positions"]]
        return data

    @post_load
    def make_object(self, data: Dict[str, str], **kwargs) -> TextPositionSet:

        return TextPositionSet(**data)


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
            schema = QuoteSchema()
            data = schema.expand_anchor_shorthand(selection)
            selection = schema.load(data)
        if isinstance(selection, TextQuoteSelector):
            selection = [selection]
        elif isinstance(selection, TextPositionSelector):
            return TextPositionSet(positions=selection)
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
