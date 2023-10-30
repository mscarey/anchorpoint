import pytest

from anchorpoint.textselectors import (
    TextQuoteSelector,
    TextPositionSelector,
    TextPositionSet,
    TextSelectionError,
)


class TestLoadSelector:
    def test_schema_loads_position_selector(self):
        data = {"start": 0, "end": 12}
        result = TextPositionSelector(**data)
        assert isinstance(result, TextPositionSelector)

    def test_selector_from_string(self):
        data = "eats,|shoots,|and leaves"
        result = TextQuoteSelector.from_text(data)
        assert result.exact == "shoots,"

    def test_selector_from_undivided_string(self):
        data = "Exactly the text I want"
        result = TextQuoteSelector.from_text(data)
        assert result.exact == "Exactly the text I want"

    def test_selector_from_string_split_wrongly(self):
        data = "eats,|shoots,|and leaves|"
        with pytest.raises(TextSelectionError):
            TextQuoteSelector.from_text(data)


class TestPositionSelector:
    def test_schema_loads_position_selector(self):
        data = {"start": 0, "end": 12}
        result = TextPositionSelector(**data)
        assert isinstance(result, TextPositionSelector)

    def test_ordered_position_selector_fields(self):
        """Test that "start" is before "end"."""
        data = {"start": 0, "end": 12}
        loaded = TextPositionSelector(**data)
        dumped = loaded.model_dump()
        assert list(dumped.keys())[0] == "start"


class TestLoadSelectorSet:
    def test_quote_selector_not_in_list(self):
        data = {
            "quotes": {
                "suffix": ", and no Warrants shall issue",
            }
        }
        result = TextPositionSet(**data)
        assert result.quotes[0].suffix == ", and no Warrants shall issue"

    def test_set_with_selector_from_undivided_string(self):
        data = {"quotes": ["Exactly the text I want"]}
        result = TextPositionSet(**data)
        assert result.quotes[0].exact == "Exactly the text I want"

    def test_selector_set_schema_with_quote_outside_list(self):
        data = {"quotes": {"suffix": ", and no Warrants shall issue"}}
        result = TextPositionSet(**data)
        assert result.quotes[0].suffix == ", and no Warrants shall issue"


class TestDumpSelector:
    def test_dump_quote_selector(self):
        data = "eats,|shoots,|and leaves"
        loaded = TextQuoteSelector.from_text(data)
        dumped = loaded.model_dump()
        assert dumped["prefix"] == "eats,"
        assert dumped["suffix"] == "and leaves"

    def test_ordered_position_selector_fields(self):
        """Test that "start" is before "end"."""
        data = {"start": 0, "end": 12}
        loaded = TextPositionSelector(**data)
        dumped = loaded.model_dump()
        assert dumped == {"start": 0, "end": 12}
        assert list(dumped.keys())[0] == "start"
