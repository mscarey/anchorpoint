import pytest

from anchorpoint.schemas import QuoteSchema, PositionSchema
from anchorpoint.textselectors import (
    TextPositionSelector,
    TextPositionSet,
    TextSelectionError,
)


class TestLoadSelector:
    def test_schema_loads_position_selector(self):
        schema = PositionSchema()
        data = {"start": 0, "end": 12}
        result = schema.load(data)
        assert isinstance(result, TextPositionSelector)

    def test_selector_from_string(self):
        data = "eats,|shoots,|and leaves"
        schema = QuoteSchema()
        result = schema.load(data)
        assert result.exact == "shoots,"

    def test_selector_from_string_without_split(self):
        data = "promise me not to omit a single word"
        schema = QuoteSchema()
        result = schema.load(data)
        assert result.exact.startswith("promise")

    def test_selector_from_string_split_wrongly(self):
        data = "eats,|shoots,|and leaves|"
        schema = QuoteSchema()
        with pytest.raises(TextSelectionError):
            _ = schema.load(data)

    def test_load_true_as_selector(self):
        schema = PositionSchema()
        result = schema.load(True)
        assert isinstance(result, TextPositionSelector)
        assert result.start == 0
        assert result.range().end > 9999

    def test_load_false_as_selector(self):
        schema = PositionSchema()
        result = schema.load(False)
        assert result is None


class TestPositionSelector:
    def test_schema_loads_position_selector(self):
        schema = PositionSchema()
        data = {"start": 0, "end": 12}
        result = schema.load(data)
        assert isinstance(result, TextPositionSelector)

    def test_ordered_position_selector_fields(self):
        """Test that "start" is before "end"."""
        schema = PositionSchema()
        data = {"start": 0, "end": 12}
        loaded = schema.load(data)
        dumped = schema.dump(loaded)
        assert list(dumped.keys())[0] == "start"

    def test_schema_position_selector_with_type(self):
        schema = PositionSchema()
        data = {"start": 0, "end": 12}
        result = schema.load(data)
        assert type(result) == TextPositionSelector


class TestLoadSelectorSet:
    def test_quote_selector_not_in_list(self):
        data = {
            "quotes": {
                "suffix": ", and no Warrants shall issue",
            }
        }
        result = TextPositionSet(**data)
        assert result.quotes[0].suffix == ", and no Warrants shall issue"


class TestDumpSelector:
    def test_dump_quote_selector(self):
        data = "eats,|shoots,|and leaves"
        schema = QuoteSchema()
        loaded = schema.load(data)
        dumped = schema.dump(loaded)
        assert dumped["prefix"] == "eats,"
        assert dumped["suffix"] == "and leaves"

    def test_dump_position_selector(self):
        schema = PositionSchema()
        data = {"start": 0, "end": 12}
        loaded = schema.load(data)
        dumped = schema.dump(loaded)
        assert dumped == {"start": 0, "end": 12}

    def test_ordered_position_selector_fields(self):
        """Test that "start" is before "end"."""
        schema = PositionSchema()
        data = {"start": 0, "end": 12}
        loaded = schema.load(data)
        dumped = schema.dump(loaded)
        assert list(dumped.keys())[0] == "start"
