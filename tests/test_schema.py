import pytest

from anchorpoint.schemas import SelectorSchema, PositionSelectorSchema
from anchorpoint.textselectors import TextPositionSelector, TextSelectionError


class TestLoadSelector:
    def test_schema_loads_position_selector(self):
        schema = SelectorSchema()
        data = {"start": 0, "end": 12}
        result = schema.load(data)
        assert isinstance(result, TextPositionSelector)

    def test_selector_text_split(self):
        schema = SelectorSchema()
        data = {"text": "process, system,|method of operation|, concept, principle"}
        result = schema.load(data)
        assert result.exact.startswith("method")

    def test_selector_from_string(self):
        data = "eats,|shoots,|and leaves"
        schema = SelectorSchema()
        result = schema.load(data)
        assert result.exact == "shoots,"

    def test_selector_from_string_without_split(self):
        data = "promise me not to omit a single word"
        schema = SelectorSchema()
        result = schema.load(data)
        assert result.exact.startswith("promise")

    def test_selector_from_string_split_wrongly(self):
        data = "eats,|shoots,|and leaves|"
        schema = SelectorSchema()
        with pytest.raises(TextSelectionError):
            _ = schema.load(data)

    def test_load_true_as_selector(self):
        schema = SelectorSchema()
        result = schema.load(True)
        assert isinstance(result, TextPositionSelector)
        assert result.start == 0
        assert result.range().end > 9999

    def test_load_false_as_selector(self):
        schema = SelectorSchema()
        result = schema.load(False)
        assert result is None


class TestPositionSelector:
    def test_schema_loads_position_selector(self):
        schema = PositionSelectorSchema()
        data = {"start": 0, "end": 12}
        result = schema.load(data)
        assert isinstance(result, TextPositionSelector)

    def test_ordered_position_selector_fields(self):
        """Test that "start" is before "end"."""
        schema = PositionSelectorSchema()
        data = {"start": 0, "end": 12}
        loaded = schema.load(data)
        dumped = schema.dump(loaded)
        assert list(dumped.keys())[0] == "start"

    def test_schema_position_selector_with_type(self):
        schema = SelectorSchema()
        data = {"start": 0, "end": 12, "type": "TextPositionSelector"}
        result = schema.load(data)
        assert type(result) == TextPositionSelector


class TestDumpSelector:
    def test_dump_quote_selector(self):
        data = "eats,|shoots,|and leaves"
        schema = SelectorSchema()
        loaded = schema.load(data)
        dumped = schema.dump(loaded)
        assert dumped["prefix"] == "eats,"
        assert dumped["suffix"] == "and leaves"
        assert dumped["type"] == "TextQuoteSelector"

    def test_dump_position_selector(self):
        schema = SelectorSchema()
        data = {"start": 0, "end": 12}
        loaded = schema.load(data)
        dumped = schema.dump(loaded)
        assert dumped == {"start": 0, "end": 12, "type": "TextPositionSelector"}

    def test_ordered_position_selector_fields(self):
        """Test that "start" is before "end"."""
        schema = SelectorSchema()
        data = {"start": 0, "end": 12}
        loaded = schema.load(data)
        dumped = schema.dump(loaded)
        assert list(dumped.keys())[0] == "start"
