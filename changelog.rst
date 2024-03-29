Changelog
=========
0.8.2 (2023-11-06)
------------------
- bugfix: TextPositionSet init wouldn't accept serialized position selector
- pass selection to TextPositionSet init in list

0.8.1 (2023-11-05)
------------------
- fix error in specifying Pydantic version in setup.py

0.8.0 (2023-10-29)
------------------
- add tests for Python 3.12
- update models to pydantic v2
- add None checks for type checker
- fix type issue with TextPositionSet.sub()
- add type hints to TextPositionSet.from_quotes()
- replace CircleCI with GitHub CI
- remove unreachable validation check

0.7.0 (2021-10-09)
------------------
- passing TextPositionSet to from_selection_sequence doesn't cause error
- fix bug: Range with end "Inf" caused string slicing error
- add TextPositionSet.from_quotes
- remove TextSelector class
- start_less_than_end is no longer a root_validator

0.6.1 (2021-09-23)
------------------
- python-ranges by Superbird11 is imported instead of vendored

0.6.0 (2021-09-19)
------------------
- TextPositionSelector no longer inherits from Range
- TextPositionSet no longer inherits from RangeSet
- TextPositionSelector no longer has real_start and real_end that can differ from start and end
- Selectors and TextPositionSets are Pydantic models
- TextSelector is Pydantic model for either Quote or Position Selector
- remove Marshmallow schemas
- update type annotations for TextPositionSelector.from_range
- add TestQuoteSelector.as_unique_position method
- TextPositionSet can include TextQuoteSelectors
- add convert_quotes_to_positions method to TextPositionSet
- replace `TextPositionSet.selectors` field with `positions` and `quotes`
- change `as_quote_selector` method to `as_quote`
- TextPositionSet.add_margin includes quotes
- fix bug: subtracting int from selector set caused quotes to be lost
- add __ge__ and __gt__ methods for TextPositionSelector
- add Selecting Text with Anchorpoint guide

0.5.3 (2021-08-11)
------------------
- change readme to .rst
- use setup.py instead of setup.cfg

0.5.2 (2021-08-02)
------------------
- TextPositionSet can be made from list of tuples
- long passage in exception is truncated

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
