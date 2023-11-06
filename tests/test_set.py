from anchorpoint.textselectors import (
    TextPositionSelector,
    TextPositionSet,
    TextQuoteSelector,
    TextPositionSetFactory,
    Range,
)

import pytest


class TestMakeSelectorSet:
    def test_make_selector_set_from_different_selectors(self):
        quotes = [
            TextPositionSelector(start=0, end=7),
            TextQuoteSelector(exact="great"),
        ]
        factory = TextPositionSetFactory(text="Here is some great text.")
        selector_set = factory.from_selection(quotes)
        assert selector_set.ranges()[0].end == 7
        assert selector_set.ranges()[1].start == 13

    def test_make_selector_set_from_exact_strings(self):
        quotes = ["some", "text"]
        factory = TextPositionSetFactory(text="Here is some great text.")
        selector_set = factory.from_exact_strings(quotes)
        assert selector_set.ranges()[0].start == 8
        assert selector_set.ranges()[1].start == 19

    def test_make_selector_set_from_one_string(self):
        quote = "Here is some"
        factory = TextPositionSetFactory(text="Here is some great text.")
        selector_set = factory.from_selection(quote)
        assert selector_set.ranges()[0].start == 0
        assert selector_set.ranges()[0].end == 12

    def test_make_selector_set_from_factory(self):
        quotes = [
            TextPositionSelector(start=5, end=10),
            TextPositionSelector(start=20, end=30),
        ]
        group = TextPositionSet(positions=quotes)
        new_group = group + TextPositionSelector(start=2, end=8)
        assert new_group.ranges()[0].end == 10
        assert new_group.ranges()[1].start == 20

    def test_make_selector_set_with_selector_from_string(self):
        group = TextPositionSet(positions=TextPositionSelector(start=5, end=10))
        assert group.ranges()[0].start == 5

    def test_make_selector_set_from_position_selector(self):
        factory = TextPositionSetFactory(text="Here is some great text.")
        position_set = factory.from_selection(TextPositionSelector(start=5, end=10))
        assert position_set.ranges()[0].start == 5

    def test_make_selector_set_from_list_of_strings(self):
        factory = TextPositionSetFactory(text="Here is some great text.")
        position_set = factory.from_selection(["Here is some", "text."])
        assert position_set.ranges()[0].start == 0
        assert position_set.ranges()[0].end == 12

    def test_make_selector_set_from_list_of_tuples(self):
        factory = TextPositionSetFactory(text="Here is some great text.")
        position_set = factory.from_selection([(0, 12), (19, 22)])
        assert position_set.ranges()[0].start == 0
        assert position_set.ranges()[0].end == 12

    def test_make_selector_set_from_True(self):
        passage = "Here is some great text."
        factory = TextPositionSetFactory(text=passage)
        position_set = factory.from_selection(True)
        assert position_set.as_string(text=passage) == "Here is some great text."

    def test_make_selector_set_from_False(self):
        passage = "Here is some great text."
        factory = TextPositionSetFactory(text=passage)
        position_set = factory.from_selection(False)
        assert position_set.as_string(text=passage) == ""

    def test_selector_set_repr(self):
        group = TextPositionSet()
        assert repr(group).startswith("TextPositionSet")

    def test_set_from_position_and_quote_selectors(self):
        text = "red orange yellow green blue indigo violet"
        position = TextPositionSelector(start=4, end=17)
        quote = TextQuoteSelector(exact="blue indigo")
        group = TextPositionSet(positions=[position], quotes=[quote])
        assert group.as_string(text=text) == "…orange yellow…blue indigo…"
        assert (
            group.select_text(text=text, margin_width=10, margin_characters="green ")
            == "…orange yellow green blue indigo…"
        )

    def test_subtract_from_set_with_quote(self):
        text = "red orange yellow green blue indigo violet"
        position = TextPositionSelector(start=4, end=17)
        quote = TextQuoteSelector(exact="blue indigo")
        group = TextPositionSet(positions=[position], quotes=[quote])
        earlier_selectors = group - 7
        assert earlier_selectors.select_text(text) == "red orange…blue indigo…"

    def test_add_to_set_with_quote(self):
        text = "red orange yellow green blue indigo violet"
        position = TextPositionSelector(start=4, end=17)
        quote = TextQuoteSelector(exact="blue indigo")
        group = TextPositionSet(positions=[position], quotes=[quote])
        earlier_selectors = group + 2
        assert earlier_selectors.select_text(text) == "…ange yellow g…blue indigo…"

    def test_convert_quotes_to_positions(self):
        text = "red orange yellow green blue indigo violet"
        position = TextPositionSelector(start=4, end=17)
        quote = TextQuoteSelector(exact="blue indigo")
        group = TextPositionSet(positions=[position], quotes=[quote])
        new = group.convert_quotes_to_positions(text=text)
        assert new.positions[1].start == 24
        assert new.positions[1].end == 35

    def test_convert_overlapping_quotes_to_positions(self):
        text = "red orange yellow green blue indigo violet"
        position = TextPositionSelector(start=4, end=17)
        quote = TextQuoteSelector(exact="yellow green")
        group = TextPositionSet(positions=position, quotes=quote)
        new = group.convert_quotes_to_positions(text=text)
        assert len(new.positions) == 1
        assert group.as_string(text=text) == "…orange yellow green…"
        assert new.positions[0].start == 4
        assert new.positions[0].end == 23

    def test_make_position_set_from_dict(self):
        data = {"positions": [{"start": 3, "end": 15}]}
        result = TextPositionSet(**data)
        assert result.positions[0].start == 3
        assert result.positions[0].end == 15

    def test_make_quote_selector_from_string(self):
        data = {"quotes": "red|orange|yellow"}
        result = TextPositionSet(**data)
        assert result.quotes[0].exact == "orange"
        assert result.quotes[0].suffix == "yellow"

    def test_make_set_from_string(self):
        result = TextPositionSet.from_quotes("red|orange|yellow")
        assert result.quotes[0].exact == "orange"
        assert result.quotes[0].suffix == "yellow"

    def test_make_set_from_exact_strings(self):
        result = TextPositionSet.from_quotes(["red", "yellow"])
        assert result.quotes[0].exact == "red"
        assert result.quotes[1].exact == "yellow"

    def test_make_set_from_quote_and_string(self):
        result = TextPositionSet.from_quotes(
            [TextQuoteSelector(suffix="orange"), "yellow"]
        )
        assert result.quotes[0].exact == ""
        assert result.quotes[0].suffix == "orange"
        assert result.quotes[1].exact == "yellow"

    def test_pass_empty_selector_set_to_factory(self):
        factory = TextPositionSetFactory("hi")
        result = factory.from_selection(TextPositionSet())
        assert result.quotes == []
        assert result.positions == []


class TestCombineSelectorSet:
    def test_subtract_int_from_selector_set(self):
        quotes = [
            TextPositionSelector(start=5, end=10),
            TextPositionSelector(start=20, end=30),
        ]
        group = TextPositionSet(positions=quotes)
        new_group = group - 5
        assert new_group.ranges()[0].start == 0
        assert new_group.ranges()[0].end == 5

    def test_add_int_to_selector_set(self):
        quotes = [
            TextPositionSelector(start=5, end=10),
            TextPositionSelector(start=20, end=30),
        ]
        group = TextPositionSet(positions=quotes)
        new_group = group + 5
        assert new_group.ranges()[0].start == 10
        assert new_group.ranges()[0].end == 15

    def test_error_add_negative_int_to_selector_set(self):
        quotes = [
            TextPositionSelector(start=5, end=10),
            TextPositionSelector(start=20, end=30),
        ]
        group = TextPositionSet(positions=quotes)
        with pytest.raises(IndexError):
            _ = group + -15

    def test_subtract_too_much_from_selector_set(self):
        quotes = [
            TextPositionSelector(start=5, end=10),
            TextPositionSelector(start=20, end=30),
        ]
        group = TextPositionSet(positions=quotes)
        with pytest.raises(IndexError):
            _ = group - 40

    def test_make_set_from_one_selector(self):
        quote = TextPositionSelector(start=5, end=10)
        group = TextPositionSet(positions=quote)
        assert group.ranges()[0].start == 5

    def test_string_for_set(self):
        quote = TextPositionSelector(start=5, end=10)
        group = TextPositionSet(positions=quote)
        assert str(group).startswith("TextPositionSet(positions")

    def test_add_non_overlapping_sets(self):
        left = TextPositionSet(positions=TextPositionSelector(start=50, end=60))
        right = TextPositionSet(positions=TextPositionSelector(start=20, end=40))
        new = left + right
        assert isinstance(new, TextPositionSet)
        assert isinstance(new.positions[0], TextPositionSelector)
        assert len(new.positions) == 2
        assert new.positions[0].start == 20

    def test_add_overlapping_sets(self):
        left = TextPositionSet(positions=TextPositionSelector(start=40, end=60))
        right = TextPositionSet(positions=TextPositionSelector(start=50, end=80))
        new = left + right
        assert isinstance(new, TextPositionSet)
        assert isinstance(new.positions[0], TextPositionSelector)
        assert len(new.positions) == 1
        assert new.positions[0].start == 40
        assert new.positions[0].end == 80

    def test_add_selector_to_set(self):
        left = TextPositionSet(positions=TextPositionSelector(start=50, end=60))
        right = TextPositionSelector(start=20, end=40)
        new = left + right
        assert isinstance(new, TextPositionSet)
        assert isinstance(new.positions[0], TextPositionSelector)
        assert len(new.ranges()) == 2
        assert new.ranges()[0].start == 20

    def test_add_set_to_selector(self):
        left = TextPositionSelector(start=40, end=60)
        right = TextPositionSet(positions=TextPositionSelector(start=20, end=35))
        new = left + right
        assert isinstance(new, TextPositionSet)
        assert isinstance(new.positions[0], TextPositionSelector)
        assert len(new.ranges()) == 2
        assert new.ranges()[0].start == 20

    def test_subtract_set_from_set(self, make_text):
        s102b = make_text["s102b"]
        selector = TextQuoteSelector(suffix=", procedure")
        position = selector.as_position(s102b)
        selector_set = TextPositionSet(positions=position)

        to_subtract = TextQuoteSelector(exact="for an original work of authorship")
        position_to_subtract = to_subtract.as_position(s102b)
        set_to_subtract = TextPositionSet(positions=position_to_subtract)

        new_set = selector_set - set_to_subtract

        assert new_set.ranges()[0].start == 0
        assert new_set.ranges()[1].start == 71

        assert isinstance(new_set, TextPositionSet)
        assert isinstance(new_set.positions[0], TextPositionSelector)

    def test_intersection_of_set_and_selector(self, make_text):
        s102b = make_text["s102b"]
        selector = TextQuoteSelector(suffix=", procedure")
        position = selector.as_position(s102b)
        selector_set = TextPositionSet(positions=position)
        selector = TextPositionSelector(start=70, end=100)
        combined = selector_set & selector
        assert combined.ranges()[0].start == 70
        assert combined.ranges()[0].end == 90
        assert isinstance(combined, TextPositionSet)

    def test_union_of_set_and_selector(self, make_text):
        s102b = make_text["s102b"]
        selector = TextQuoteSelector(suffix=", procedure")
        position = selector.as_position(s102b)
        selector_set = TextPositionSet(positions=position)
        selector = TextPositionSelector(start=70, end=100)
        combined = selector_set | selector
        assert combined.ranges()[0].start == 0
        assert combined.ranges()[0].end == 100
        assert isinstance(combined, TextPositionSet)

    def test_make_quote_selectors_from_set(self, make_text):
        quote = TextQuoteSelector(exact="United States", suffix=" and subject")
        position = quote.as_position(make_text["amendment"])
        position_set = TextPositionSet(positions=position)
        new_quotes = position_set.as_quotes(make_text["amendment"])
        assert new_quotes[0].exact == "United States"
        assert new_quotes[0].prefix.strip().endswith("in the")


class TestCompareSelectorSet:
    def test_full_passage_implies_selections(self, make_text):
        passage = make_text["s102b"]
        factory = TextPositionSetFactory(text=passage)
        selector_set = factory.from_quote_selectors(
            [
                TextQuoteSelector(exact="In no case does copyright protection"),
                TextQuoteSelector(exact="extend to any idea"),
            ]
        )
        full_passage = TextPositionSet(
            positions=[TextPositionSelector(start=0, end=200)]
        )
        assert full_passage > selector_set
        assert full_passage >= selector_set

    def test_compare_to_empty_regular_set(self):
        wide_range = Range(start=0, end=200)
        full_passage = TextPositionSet.from_ranges(wide_range)
        regular_set = set()
        assert full_passage > regular_set
        assert full_passage >= regular_set

    def test_add_blank_margin(self):
        selector_set = TextPositionSet(
            positions=[
                TextPositionSelector(start=0, end=4),
                TextPositionSelector(start=5, end=10),
            ]
        )
        passage = "Some text."
        assert selector_set.as_string(text=passage) == "Some…text."
        result = selector_set.add_margin(text=passage, margin_width=1)
        assert result.as_string(text=passage) == "Some text."

    def test_cannot_add_negative_margin(self):
        passage = "Some text."
        selector_set = TextPositionSet(
            positions=[
                TextPositionSelector(start=0, end=4),
                TextPositionSelector(start=5, end=10),
            ]
        )
        with pytest.raises(ValueError):
            selector_set.add_margin(text=passage, margin_width=-1)

    def test_add_margin_with_characters(self):
        selector_set = TextPositionSet(
            positions=[
                TextPositionSelector(start=0, end=7),
                TextPositionSelector(start=11, end=21),
            ]
        )
        passage = 'a quote.") Therefore,'
        assert selector_set.as_string(text=passage) == "a quote…Therefore,"
        result = selector_set.add_margin(text=passage, margin_width=4)
        assert result.as_string(text=passage) == 'a quote.") Therefore,'

    def test_same_selector_set(self):
        selector_set = TextPositionSet(
            positions=[
                TextPositionSelector(start=0, end=4),
                TextPositionSelector(start=5, end=10),
            ]
        )
        other_set = TextPositionSet(
            positions=[
                TextPositionSelector(start=5, end=10),
                TextPositionSelector(start=0, end=4),
            ]
        )
        assert selector_set == other_set
        assert selector_set >= other_set

    def test_set_greater_than_selector(self):
        selector_set = TextPositionSet(
            positions=[
                TextPositionSelector(start=0, end=4),
                TextPositionSelector(start=5, end=10),
            ]
        )
        other_selector = TextPositionSelector(start=6, end=10)
        assert selector_set > other_selector
        assert selector_set >= other_selector


class TestTextFromSelectorSet:
    def test_get_text_selection_from_set(self, make_text):
        passage = make_text["s102b"]
        factory = TextPositionSetFactory(text=passage)
        selector_set = factory.from_quote_selectors(
            [
                TextQuoteSelector(exact="In no case does copyright protection"),
                TextQuoteSelector(exact="extend to any idea"),
            ]
        )
        result = selector_set.as_string(text=passage)
        assert result == "In no case does copyright protection…extend to any idea…"

    def test_serialize_set_with_pydantic(self):
        selector_set = TextPositionSet(
            positions=[
                TextPositionSelector(start=0, end=4),
                TextPositionSelector(start=5, end=10),
            ]
        )
        assert selector_set.model_dump()["positions"][0]["end"] == 4

    def test_get_schema_with_pydantic(self):
        assert (
            TextPositionSet.model_json_schema()["properties"]["positions"]["items"][
                "$ref"
            ]
            == "#/$defs/TextPositionSelector"
        )

    def test_set_as_text_sequence_with_no_endpoint(self):
        """Test whether a Range with end "Inf" causes a string slicing error."""
        obj = TextPositionSet(
            positions=[TextPositionSelector(start=0, end=None)], quotes=[]
        )
        text = "The right of the people to be secure in their persons"
        assert (
            str(obj.as_text_sequence(text=text))
            == "The right of the people to be secure in their persons"
        )
