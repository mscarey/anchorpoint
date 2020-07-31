from anchorpoint.textselectors import TextPositionSelector
from marshmallow import ValidationError
import pytest

from anchorpoint.schemas import SelectorSchema


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
        with pytest.raises(ValidationError):
            _ = schema.load(data)

    def test_load_true_as_selector(self):
        schema = SelectorSchema()
        result = schema.load(True)
        assert isinstance(result, TextPositionSelector)
        assert result.start == 0
        assert result.end > 9999

    def test_load_false_as_selector(self):
        schema = SelectorSchema()
        result = schema.load(False)
        assert result is None


class TestDumpSelector:
    def test_dump_quote_selector(self):
        data = "eats,|shoots,|and leaves"
        schema = SelectorSchema()
        loaded = schema.load(data)
        dumped = schema.dump(loaded)
        assert dumped["prefix"] == "eats,"
        assert dumped["suffix"] == "and leaves"

    def test_dump_position_selector(self):
        schema = SelectorSchema()
        data = {"start": 0, "end": 12}
        loaded = schema.load(data)
        dumped = schema.dump(loaded)
        assert dumped == {
            "start": 0,
            "end": 12,
            "include_start": True,
            "include_end": False,
        }
