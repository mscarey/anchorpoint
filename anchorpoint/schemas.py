"""Schema for serializing text selectors."""

from typing import Dict, List, Mapping, Optional, Sequence, TypedDict, Union

from anchorpoint.textselectors import (
    TextQuoteSelector,
    TextPositionSelector,
    TextPositionSet,
)


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
