from typing import Dict

import pytest


@pytest.fixture(scope="module")
def make_text() -> Dict[str, str]:
    """
    Text passages to practice quoting from.
    """

    return {
        "s102b": (
            "In no case does copyright protection for an original "
            + "work of authorship extend to any idea, procedure, process, system, "
            + "method of operation, concept, principle, or discovery, regardless of "
            + "the form in which it is described, explained, illustrated, or "
            + "embodied in such work."
        ),
        "amendment": (
            "All persons born or naturalized in the United States "
            "and subject to the jurisdiction thereof, are citizens "
            "of the United States and of the State wherein they reside. "
            "No State shall make or enforce any law which shall abridge "
            "the privileges or immunities of citizens of the United States; "
            "nor shall any State deprive any person of life, liberty, or "
            "property, without due process of law; nor deny to any person "
            "within its jurisdiction the equal protection of the laws."
        ),
    }
