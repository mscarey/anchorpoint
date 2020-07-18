# Anchorpoint

[![CircleCI](https://circleci.com/gh/mscarey/anchorpoint.svg?style=svg)](https://circleci.com/gh/mscarey/anchorpoint) [![Coverage Status](https://coveralls.io/repos/github/mscarey/anchorpoint/badge.svg?branch=master)](https://coveralls.io/github/mscarey/anchorpoint?branch=master)

Anchorpoint supplies TextQuoteSelector and TextPositionSelector classes based on the Web Annotation Data Model, which is a [W3C Recommendation](https://www.w3.org/TR/annotation-model/). Anchorpoint includes helper methods for switching between selector types, and a [marshmallow](https://marshmallow.readthedocs.io/) schema for serialization. Anchorpoint is used by [legislice](https://github.com/mscarey/legislice) for referencing laws such as statutes, and by [AuthoritySpoke](https://authorityspoke.readthedocs.io) for referencing judicial opinions.

[API Documentation](https://anchorpoint.readthedocs.io) is available on readthedocs.

Anchorpoint relies on [python-ranges](https://github.com/Superbird11/ranges) to perform set operations on spans of text.

## Related Packages

In Javascript, try the [Text Quote Anchor](https://www.npmjs.com/package/dom-anchor-text-quote) and [Text Position Anchor](https://www.npmjs.com/package/dom-anchor-text-position) packages.

In Python try [python-ranges](https://github.com/Superbird11/ranges), which is the basis for much of the TextPositionSelector class's behavior.
