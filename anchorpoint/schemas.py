"""Schema for serializing text selectors."""

from typing import Dict, List, Tuple, Union

from marshmallow import Schema, fields, post_load, pre_load

from anchorpoint.textselectors import TextQuoteSelector, TextPositionSelector


class SelectorSchema(Schema):
    r"""
    Schema for loading a TextQuoteSelector or TextPositionSelector.

    Generates a :class:`~anchorpoint.textselectors.TextQuoteSelector`
    if the input data contains any of the fields "exact", "prefix",
    or "suffix", and returns a
    :class:`~anchorpoint.textselectors.TextPositionSelector` otherwise.

    """
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

    @pre_load
    def preprocess_data(
        self, data: Union[str, Dict[str, Union[str, Dict, List]]], **kwargs
    ) -> Dict[str, Union[str, List]]:
        data = self.expand_anchor_shorthand(data)

        return data

    @post_load
    def make_object(self, data, **kwargs):
        if data.get("exact") or data.get("prefix") or data.get("suffix"):
            model = TextQuoteSelector
            for unwanted in ("start", "end", "include_start", "include_end"):
                data.pop(unwanted, None)
        else:
            model = TextPositionSelector
            for unwanted in ("exact", "prefix", "suffix"):
                data.pop(unwanted, None)
        return model(**data)
