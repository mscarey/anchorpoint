Anchorpoint
===========

A Python library for anchoring annotations with text substring selectors.

.. image:: https://img.shields.io/badge/open-ethical-%234baaaa
    :target: https://ethicalsource.dev/licenses/
    :alt: An Ethical Open Source Project

.. image:: https://coveralls.io/repos/github/mscarey/anchorpoint/badge.svg?branch=master
    :target: https://coveralls.io/github/mscarey/anchorpoint?branch=master
    :alt: Test Coverage Percentage

.. image:: https://github.com/mscarey/anchorpoint/actions/workflows/python-package.yml/badge.svg
    :target: https://github.com/mscarey/anchorpoint/actions
    :alt: GitHub Actions Workflow

.. image:: https://readthedocs.org/projects/anchorpoint/badge/?version=latest
    :target: https://anchorpoint.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Anchorpoint supplies TextQuoteSelector and TextPositionSelector
classes based on the Web Annotation Data Model, which is
a `W3C Recommendation`_. Anchorpoint includes helper methods
for switching between selector types, and
a `pydantic`_ schema for serialization. Anchorpoint is used
by `Legislice`_ for referencing laws such as statutes, and
by `AuthoritySpoke`_ for referencing judicial opinions.

`API Documentation`_ is available on readthedocs.

Anchorpoint relies on `python-ranges`_ to perform set operations on spans of text.

Related Packages
~~~~~~~~~~~~~~~~

In Javascript, try the `Text Quote Anchor`_ and `Text Position Anchor`_ packages.

In Python try python-ranges_, which is the basis for much of the TextPositionSelector class's behavior.

.. _W3C Recommendation: https://www.w3.org/TR/annotation-model/
.. _pydantic: https://docs.pydantic.dev/latest/
.. _Legislice: https://github.com/mscarey/legislice
.. _AuthoritySpoke: https://authorityspoke.readthedocs.io
.. _API Documentation: https://anchorpoint.readthedocs.io/en/latest/
.. _python-ranges: https://github.com/Superbird11/ranges
.. _Text Quote Anchor: https://www.npmjs.com/package/dom-anchor-text-quote
.. _Text Position Anchor: https://www.npmjs.com/package/dom-anchor-text-position