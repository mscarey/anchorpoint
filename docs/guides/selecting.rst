===============================
Selecting Text with Anchorpoint
===============================

Anchorpoint is a tool for labeling referenced passages within text documents,
in a format that allows the "anchors" to the referenced passages to be stored
and transmitted separately from the documents themselves. Anchorpoint has two
basic ways of selecting text: as text positions, or as text quotes. Here's a demonstration
of creating a text string in Python and then using both kinds of text selectors.

    >>> from anchorpoint import TextPositionSelector, TextQuoteSelector
    >>> legal_text = (
    ...    "Copyright protection subsists, in accordance with this title, "
    ...     "in original works of authorship fixed in any tangible medium of expression, "
    ...     "now known or later developed, from which they can be perceived, reproduced, "
    ...     "or otherwise communicated, either directly or with the aid of a machine or device. "
    ...     "Works of authorship include the following categories: "
    ...     "literary works; musical works, including any accompanying words; "
    ...     "dramatic works, including any accompanying music; "
    ...     "pantomimes and choreographic works; "
    ...     "pictorial, graphic, and sculptural works; "
    ...     "motion pictures and other audiovisual works; "
    ...     "sound recordings; and architectural works.")
    >>> positions = TextPositionSelector(start=65, end=93)
    >>> positions.select_text(legal_text)
    'original works of authorship'
    >>> quote = TextQuoteSelector(exact="in accordance with this title")
    >>> quote.select_text(legal_text)
    'in accordance with this title'

A :class:`~anchorpoint.textselectors.TextPositionSelector` works by identifying the positions of
the start and end characters within the text string object, while
a :class:`~anchorpoint.textselectors.TextQuoteSelector` describes the part of the text
that is being selected.

Sometimes a selected passage is too long to include in full in
the :class:`~anchorpoint.textselectors.TextQuoteSelector`\.
In that case, you can identify the selection by specifying its ``prefix`` and ``suffix``.
That is, the text immediately before and immediately after the text you want to select.

    >>> quote = TextQuoteSelector(prefix="otherwise communicated, ", suffix=" Works of authorship")
    >>> quote.select_text(legal_text)
    'either directly or with the aid of a machine or device.'

If you specify just a suffix, then the start of your text selection is the beginning
of the text string. If you specify just a prefix, then your text selection continues to the end
of the text string.

    >>> quote_from_start = TextQuoteSelector(suffix="in accordance with this title")
    >>> quote_from_start.select_text(legal_text)
    'Copyright protection subsists,'
    >>> quote_from_end = TextQuoteSelector(prefix="sound recordings; and")
    >>> quote_from_end.select_text(legal_text)
    'architectural works.'

If you want to use a :class:`~anchorpoint.textselectors.TextQuoteSelector` to select
a particular instance of a phrase that appears more than once in the text, then you
can add a ``prefix`` or ``suffix`` in addition to the ``exact`` phrase to eliminate the
ambiguity. For example, this selector applies to the second instance of the word
"authorship" in the text, not the first instance.

    >>> authorship_selector = TextQuoteSelector(exact="authorship", suffix="include")
    >>> authorship_selector.select_text(legal_text)
    'authorship'

Converting Between Selector Types
---------------------------------

You can use the :meth:`~anchorpoint.textselectors.TextQuoteSelector.as_position` and
:meth:`~anchorpoint.textselectors.TextPositionSelector.as_quote` methods
to convert between the two types of selector.

    >>> authorship_selector.as_position(legal_text)
    TextPositionSelector(start=306, end=316)
    >>> positions.as_quote(legal_text)
    TextQuoteSelector(exact='original works of authorship', prefix='', suffix='')

Combining and Grouping Selectors
--------------------------------

Position selectors can be combined into a single selector that covers both spans of text.

    >>> left = TextPositionSelector(start=5, end=22)
    >>> right = TextPositionSelector(start=12, end=27)
    >>> left + right
    TextPositionSelector(start=5, end=27)

If two position selectors don't overlap, then adding them returns a different
class called a :class:`~anchorpoint.textselectors.TextPositionSet`\.

    >>> from anchorpoint import TextPositionSet
    >>> left = TextPositionSelector(start=65, end=79)
    >>> right = TextPositionSelector(start=100, end=136)
    >>> selector_set = left + right
    >>> selector_set
    TextPositionSet(positions=[TextPositionSelector(start=65, end=79), TextPositionSelector(start=100, end=136)], quotes=[])

The :class:`~anchorpoint.textselectors.TextPositionSet` can be used to select nonconsecutive passages of text.

    >>> selector_set.select_text(legal_text)
    '…original works…in any tangible medium of expression…'

If needed, you can use a :class:`~anchorpoint.textselectors.TextPositionSet` to
select text with a combination of both positions and quotes.

    >>> text = "red orange yellow green blue indigo violet"
    >>> position = TextPositionSelector(start=4, end=17)
    >>> quote = TextQuoteSelector(exact="blue indigo")
    >>> group = TextPositionSet(positions=[position], quotes=[quote])
    >>> group.select_text(text)
    '…orange yellow…blue indigo…'

You can also add or subtract an integer to move the text selection left or right, but
only the position selectors will be moved, not the quote selectors.

    >>> earlier_selectors = group - 7
    >>> earlier_selectors.select_text(text)
    'red orange…blue indigo…'

Union and intersection operators also work.

    >>> left = TextPositionSelector(start=2, end=10)
    >>> right = TextPositionSelector(start=5, end=20)
    >>> left & right
    TextPositionSelector(start=5, end=10)

Comparing Selectors and Sets
----------------------------

The greater than and less than operators can be used to check whether one selector
or set covers the entire range of another. This is used to check whether one selector
only contains text that's already within another selector.

    >>> smaller = TextPositionSelector(start=4, end=8)
    >>> overlapping = TextPositionSelector(start=6, end=50)
    >>> overlapping > smaller
    False
    >>> superset = TextPositionSelector(start=0, end=10)
    >>> superset > smaller
    True

TextPositionSets also have a :meth:`~anchorpoint.textselectors.TextPositionSet.__gt__` method
that works in the same way.

    >>> selector_set > TextPositionSelector(start=100, end=110)
    True

Serializing Selectors
---------------------

Anchorpoint uses `Pydantic <https://pydantic-docs.helpmanual.io/>`__ to
serialize selectors either to Python dictionaries
or to JSON strings suitable for sending over the internet with APIs.

    >>> authorship_selector.model_dump_json()
    '{"exact": "authorship", "prefix": "", "suffix": "include"}'
    >>> selector_set.model_dump()
    {'positions': [{'start': 65, 'end': 79}, {'start': 100, 'end': 136}], 'quotes': []}

Pydantic's data loading methods mean that you can also create the data for an
Anchorpoint selector using nested dictionaries, and then load it with the class's
constructor method.

    >>> data = {'positions': [{'start': 65, 'end': 79}, {'start': 100, 'end': 136}]}
    >>> TextPositionSet(**data)
    TextPositionSet(positions=[TextPositionSelector(start=65, end=79), TextPositionSelector(start=100, end=136)], quotes=[])

You can also `get a valid OpenAPI schema <https://pydantic-docs.helpmanual.io/usage/schema/>`__,
for using Anchorpoint selectors in an API that you design.

    >>> TextPositionSelector.schema_json()
    '{"title": "TextPositionSelector", "description": "Describes a textual segment by start and end positions.\\n\\nBased on the Web Annotation Data Model `Text Position Selector\\n<https://www.w3.org/TR/annotation-model/#text-position-selector>`_ standard\\n\\n:param start:\\n    The starting position of the segment of text.\\n    The first character in the full text is character position 0,\\n    and the character is included within the segment.\\n\\n:param end:\\n    The end position of the segment of text.\\n    The character is not included within the segment.", "type": "object", "properties": {"start": {"title": "Start", "default": 0, "type": "integer"}, "end": {"title": "End", "type": "integer"}}}'