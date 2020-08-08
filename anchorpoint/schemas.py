"""Schema for serializing text selectors."""

from typing import Dict, List, Optional, Sequence, Union

from marshmallow import Schema, fields, post_load, pre_load

from anchorpoint.textselectors import (
    TextQuoteSelector,
    TextPositionSelector,
    TextPositionSet,
)


class SelectorSchema(Schema):
    r"""
    Schema for loading a TextQuoteSelector or TextPositionSelector.

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
    end = fields.Int(optional=True)
    include_start = fields.Bool(missing=True)
    include_end = fields.Bool(missing=False)

    def expand_anchor_shorthand(
        self, data: Union[str, Dict[str, str]]
    ) -> Dict[str, str]:
        """
        Convert input from shorthand format to normal selector format.


        .. code-block:: python

            >>> schema = SelectorSchema()
            >>> schema.expand_anchor_shorthand("eats,|shoots,|and leaves")
            {'exact': 'shoots,', 'prefix': 'eats,', 'suffix': 'and leaves'}
        """
        if isinstance(data, str):
            data = {"text": data}
        text = data.get("text")
        if text:
            (
                data["prefix"],
                data["exact"],
                data["suffix"],
            ) = TextQuoteSelector.split_anchor_text(text)
            del data["text"]
        return data

    def convert_bool_to_dict(self, data: bool) -> Dict[str, int]:
        """Interpret True as a TextPositionSelector including the whole section."""

        if data is True:
            return {"start": 0}
        return {"start": 0, "end": 0}

    @pre_load
    def preprocess_data(
        self, data: Union[str, Dict[str, Union[str, Dict, List]]], **kwargs
    ) -> Dict[str, Union[str, List]]:
        if isinstance(data, bool):
            data = self.convert_bool_to_dict(data)
        if data:
            data = self.expand_anchor_shorthand(data)

        return data

    @post_load
    def make_object(
        self, data, **kwargs
    ) -> Optional[Union[TextPositionSelector, TextQuoteSelector]]:
        if data.get("exact") or data.get("prefix") or data.get("suffix"):
            model = TextQuoteSelector
            for unwanted in ("start", "end", "include_start", "include_end"):
                data.pop(unwanted, None)
        else:
            model = TextPositionSelector
            if data.get("start") == data.get("end"):
                return None
            for unwanted in ("exact", "prefix", "suffix"):
                data.pop(unwanted, None)
        return model(**data)


class TextPositionSetFactory:
    def __init__(self, passage: str) -> None:
        self.passage = passage

    def from_selection(
        self,
        selection: Union[
            bool,
            str,
            TextPositionSelector,
            TextQuoteSelector,
            Sequence[TextQuoteSelector],
        ],
    ) -> TextPositionSet:
        """Construct TextPositionSet for a provided text passage, from any type of selector."""
        if selection is True:
            return TextPositionSet(TextPositionSelector(0, len(self.passage)))
        elif selection is False:
            return TextPositionSet()
        if isinstance(selection, str):
            schema = SelectorSchema()
            selection = schema.load(selection)
        if isinstance(selection, TextQuoteSelector):
            selection = [selection]
        elif isinstance(selection, TextPositionSelector):
            selection = TextPositionSet(selection)
        if isinstance(selection, Sequence) and all(
            isinstance(item, TextQuoteSelector) for item in selection
        ):
            selection = self.from_quote_selectors(quotes=selection)
        if not isinstance(selection, TextPositionSet):
            selection = TextPositionSet(selection)
        return selection

    def from_quote_selectors(
        self, quotes: Sequence[TextQuoteSelector]
    ) -> TextPositionSet:
        position_selectors = [quote.as_position(self.passage) for quote in quotes]
        return TextPositionSet(position_selectors)
