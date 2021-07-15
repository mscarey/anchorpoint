0.5.1 (2021-05-15)
------------------
- improper shorthand for selector raises TextSelectionError

0.5.0 (2021-05-07)
------------------
- add TextPositionSelector.from_text constructor
- Range constructor interprets None as 0
- fix bug: union with TextPositionSet should return TextPositionSet
- add PositionSelectorSchema, for when a selector can't be a TextQuoteSelector

0.4.4 (2021-01-25)
------------------
- provide "missing" instead of "optional" argument for marshmallow schema
- add TextPositionSetFactory.from_exact_strings
- SelectorSchema.expand_anchor_shorthand takes only a string argument
- TextPositionSetFactory.from_selection will accept a Sequence of mixed types

0.4.3 (2020-12-11)
------------------
- TextPositionSelector serializer dumps .real_start and .real_end
- TextPositionSelector serializer omits "include_start" and "include_end"
- TextPositionSelector serializer orders fields so "start" comes before "end"
- disallow zero-length TextPositionSelectors

0.4.2 (2020-08-30)
------------------
- create TextPositionSelector .real_start and .real_end
- create TextPositionSet.add_margin

0.4.1 (2020-08-29)
------------------
- TextPositionSetFactory will accept list of strings
- subtracting more than start value is no longer IndexError, but more than end value is
- TextSequence quoting from empty string doesn't start with None

0.4.0 (2020-08-08)
------------------
- TextPositionSet can output a TextSequence
- create TextSequence addition method

0.3.3 (2020-07-28)
------------------
- fix bug: leading whitespace when selecting from prefix

0.3.2 (2020-07-22)
------------------
- fix bug where adding selectors converted them to parent class
- add TextSelectionError exception

0.3.1 (2020-07-19)
------------------
- add left and right margin parameters to TextPositionSelector.as_quote_selector
- as_quotes method for TextSelectorSet
- enable adding int to TextSelectorSet
- fix class name in repr for TextSelectorSet

0.3.0 (2020-07-18)
------------------
- add TextQuoteSelector.from_text shortcut
- add ability to subtract an integer from all values in a TextPositionSet
- include [marshmallow](https://github.com/marshmallow-code/marshmallow) schema for serializing

0.2.1 (2020-05-21)
------------------
- add init file to utils directory

0.2.0 (2020-05-21)
------------------
- Make TextPositionSelector subclass `Range` from [python-ranges](https://github.com/Superbird11/ranges).

0.1.1 (2019-12-01)
------------------
- add init file to tests directory

0.1.0 (2019-11-30)
------------------
- Create TextPositionSelector and TextQuoteSelector classes
