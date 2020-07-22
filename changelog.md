Changelog
=========
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
-----------
- Make TextPositionSelector subclass `Range` from [python-ranges](https://github.com/Superbird11/ranges).

0.1.1 (2019-12-01)
------------------
- add init file to tests directory

0.1.0 (2019-11-30)
------------------
- Create TextPositionSelector and TextQuoteSelector classes
