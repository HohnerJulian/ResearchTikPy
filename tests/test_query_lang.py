import pytest

from researchtikpy import Query, Condition, Fields, Operators, RegionCodes, VideoLengths
from researchtikpy.query_lang import as_dict

@pytest.mark.parametrize("expected, actual", [
    pytest.param(
        {"and": [{"field_name": "hashtag_name", "operation": "IN", "field_values": ["#python"]}], "or": [], "not": []},
        Query(and_=[Condition(Fields.hashtag_name, Operators.isin, ["#python"])]),
        id="hashtag_and"
    ),
    pytest.param(
        {"and": [], "or": [{"field_name": "hashtag_name", "operation": "IN", "field_values": ["#python"]}], "not": []},
        Query(or_=[Condition(Fields.hashtag_name, Operators.isin, ["#python"])]),
        id="hashtag_or"
    ),
    pytest.param(
        {"and": [], "or": [], "not": [{"field_name": "hashtag_name", "operation": "IN", "field_values": ["#python"]}]},
        Query(not_=[Condition(Fields.hashtag_name, Operators.isin, ["#python"])]),
        id="hashtag_not"
    ),
    pytest.param(
        {"and": [
            {"field_name": "keyword", "operation": "EQ", "field_values": ["enemenemuh"]},
            {"field_name": "username", "operation": "EQ", "field_values": ["ernie_und_bert"]},
        ], "or": [], "not": []},
        Query(and_=[
            Condition(Fields.keyword, Operators.equals, ["enemenemuh"]),
            Condition(Fields.username, Operators.equals, ["ernie_und_bert"])
        ]),
        id="keyword_and_username"
    ),
    pytest.param(
        {"and": [
            {"field_name": "video_length", "operation": "EQ", "field_values": ["SHORT"]},
            {"field_name": "username", "operation": "EQ", "field_values": ["ernie_und_bert"]},
        ], "or": [], "not": []},
        Query(and_=[
            Condition(Fields.video_length, Operators.equals, [VideoLengths.SHORT]),
            Condition(Fields.username, Operators.equals, ["ernie_und_bert"])
        ]),
        id="video_length_and_username"
    ),
    pytest.param(
        {"and": [
            {"field_name": "keyword", "operation": "EQ", "field_values": ["enemenemuh"]},
            {"field_name": "region_code", "operation": "EQ", "field_values": ["DE"]},
        ], "or": [], "not": []},
        Query(and_=[
            Condition(Fields.keyword, Operators.equals, ["enemenemuh"]),
            Condition(Fields.region_code, Operators.equals, [RegionCodes.DE])
        ]),
        id="keyword_and_region_code"
    ),
])
def test_query_builder(expected, actual):
    assert expected == as_dict(actual)

@pytest.mark.parametrize("actual", [
    pytest.param({"and": [{"field_name": "nope", "operation": "IN", "field_values": ["bibo"]}], "or": [], "not": []}, id="wrong_field_name"),
    pytest.param({"and": [{"field_name": "keyword", "operation": "==", "field_values": ["bibo"]}], "or": [], "not": []}, id="wrong_operator"),
])
def test_query_builder_invalid(actual):
    with pytest.raises(ValueError):
        Query(**actual)
