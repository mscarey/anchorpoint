from typing import Dict, List, Tuple, Union

from marshmallow import Schema, fields, post_load, pre_load
from marshmallow import ValidationError

from anchorpoint.textselectors import (
    TextQuoteSelector,
    TextPositionSelector,
    TextPositionSet,
)


def split_anchor_text(text: str) -> Tuple[str, ...]:
    """
    Break up shorthand text selector format into three fields.

    Tries to break up the  string into :attr:`~TextQuoteSelector.prefix`,
    :attr:`~TextQuoteSelector.exact`,
    and :attr:`~TextQuoteSelector.suffix`, by splitting on the pipe characters.

    :param text: a string or dict representing a text passage

    :returns: a tuple of the three values
    """

    if text.count("|") == 0:
        return ("", text, "")
    elif text.count("|") == 2:
        return tuple([*text.split("|")])
    raise ValidationError(
        "If the 'text' field is included, it must be either a dict "
        + "with one or more of 'prefix', 'exact', and 'suffix' "
        + "a string containing no | pipe "
        + "separator, or a string containing two pipe separators to divide "
        + "the string into 'prefix', 'exact', and 'suffix'."
    )


class SelectorSchema(Schema):

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
        """
        if isinstance(data, str):
            data = {"text": data}
        text = data.get("text")
        if text:
            data["prefix"], data["exact"], data["suffix"] = split_anchor_text(text)
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
