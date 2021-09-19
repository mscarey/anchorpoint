==============
Selecting Text
==============

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
In that case, you can identify the selection by specifying its `prefix` and `suffix`.
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
can add a `prefix` or `suffix` in addition to the `exact` phrase to eliminate the
ambiguity. For example, this selector applies to the second instance of the word
"authorship" in the text, not the first instance.

    >>> authorship_selector = TextQuoteSelector(exact="authorship", suffix="include")
    >>> authorship_selector.select_text(legal_text)
    'authorship'

Converting Between Selector Types
---------------------------------

The :meth:`~anchorpoint.textselectors.TextQuoteSelector.as_position` and
:meth:`~anchorpoint.textselectors.TextPositionSelector.as_quote` methods can
be used to convert between the two types of selector.

    >>> authorship_selector.as_position(legal_text)
    TextPositionSelector(start=306, end=316)
    >>> positions.as_quote(legal_text)
    TextQuoteSelector(exact='original works of authorship', prefix='', suffix='')
