import os
import pytest
from mkdocs_yaml_schema_plugin.markdown import markdown_gen, extract_yaml_section

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
SAMPLE_SCHEMA = os.path.join(FIXTURE_DIR, "sample.schema.yaml")


# ---------------------------------------------------------------------------
# extract_yaml_section
# ---------------------------------------------------------------------------

def test_extract_yaml_section_empty_parts_returns_data():
    data = {"a": 1}
    assert extract_yaml_section([], data) == {"a": 1}


def test_extract_yaml_section_single_part():
    data = {"properties": {"host": {"type": "string"}}}
    result = extract_yaml_section(["properties"], data)
    assert result == {"host": {"type": "string"}}


def test_extract_yaml_section_nested_parts():
    data = {"properties": {"database": {"properties": {"host": {"type": "string"}}}}}
    result = extract_yaml_section(["properties", "database", "properties"], data)
    assert result == {"host": {"type": "string"}}


# ---------------------------------------------------------------------------
# markdown_gen.safe_get_value
# ---------------------------------------------------------------------------

def test_safe_get_value_existing_key():
    gen = markdown_gen()
    value, found = gen.safe_get_value({"key": "val"}, "key")
    assert found is True
    assert value == "val"


def test_safe_get_value_missing_key():
    gen = markdown_gen()
    value, found = gen.safe_get_value({"key": "val"}, "missing")
    assert found is False
    assert value is None


def test_safe_get_value_none_data():
    gen = markdown_gen()
    value, found = gen.safe_get_value(None, "key")
    assert found is False
    assert value is None


# ---------------------------------------------------------------------------
# markdown_gen.set_config
# ---------------------------------------------------------------------------

def test_set_config_builds_yaml_config():
    gen = markdown_gen()
    gen.set_config({"yaml_files": [{"file": "schema.yaml", "tag": "MYSCHEMA"}]})
    assert len(gen.yaml_config) == 1
    assert gen.yaml_config[0]["file"] == "schema.yaml"
    assert gen.yaml_config[0]["tag"] == "MYSCHEMA"


def test_set_config_regex_matches_simple_tag():
    gen = markdown_gen()
    gen.set_config({"yaml_files": [{"file": "schema.yaml", "tag": "MYSCHEMA"}]})
    import re
    pattern = gen.yaml_config[0]["regex"]
    assert re.search(pattern, "#MYSCHEMA#")
    assert re.search(pattern, "#MYSCHEMA__subsection#")
    assert not re.search(pattern, "#OTHERTAG#")


def test_set_config_empty_yaml_files():
    gen = markdown_gen()
    gen.set_config({"yaml_files": []})
    assert gen.yaml_config == []


# ---------------------------------------------------------------------------
# markdown_gen.markdown_for_items
# ---------------------------------------------------------------------------

SIMPLE_ITEMS = {
    "properties": {
        "host": {"type": "string", "description": "The host"},
        "port": {"type": "integer", "description": "The port"},
    }
}


def test_markdown_for_items_header():
    gen = markdown_gen()
    result = gen.markdown_for_items("root", SIMPLE_ITEMS)
    assert "| Key | Type | Description |" in result
    assert "| --- | --- | --- |" in result


def test_markdown_for_items_simple_types():
    gen = markdown_gen()
    result = gen.markdown_for_items("root", SIMPLE_ITEMS)
    assert "| host | string |" in result
    assert "| port | integer |" in result


def test_markdown_for_items_oneof_type():
    gen = markdown_gen()
    items = {
        "properties": {
            "retries": {
                "oneOf": [{"type": "integer"}, {"type": "null"}],
                "description": "Number of retries",
            }
        }
    }
    result = gen.markdown_for_items("root", items)
    assert "| retries | integer, null |" in result


def test_markdown_for_items_anyof_type():
    gen = markdown_gen()
    items = {
        "properties": {
            "format": {
                "anyOf": [{"type": "string"}, {"type": "null"}],
                "description": "Log format",
            }
        }
    }
    result = gen.markdown_for_items("root", items)
    assert "| format | string, null |" in result


def test_markdown_for_items_bold_keywords():
    gen = markdown_gen()
    items = {
        "properties": {
            "retries": {
                "type": "integer",
                "description": "Retries. NOTE: Keep low. RECOMMENDATION: Use 3.",
            }
        }
    }
    result = gen.markdown_for_items("root", items)
    assert "**NOTE:**" in result
    assert "**RECOMMENDATION:**" in result


def test_markdown_for_items_newline_to_br():
    gen = markdown_gen()
    items = {
        "properties": {
            "level": {
                "type": "string",
                "description": "Line one\nLine two",
            }
        }
    }
    result = gen.markdown_for_items("root", items)
    assert "<br />" in result


# ---------------------------------------------------------------------------
# markdown_gen.get_markdown (integration with fixture file)
# ---------------------------------------------------------------------------

def _make_gen(tag, schema_file):
    gen = markdown_gen()
    gen.set_config({"yaml_files": [{"file": schema_file, "tag": tag}]})
    return gen


def test_get_markdown_replaces_tag():
    gen = _make_gen("SAMPLE", SAMPLE_SCHEMA)
    result = gen.get_markdown("#SAMPLE__database#")
    assert "#SAMPLE__database#" not in result
    assert "| Key | Type | Description |" in result


def test_get_markdown_database_section():
    gen = _make_gen("SAMPLE", SAMPLE_SCHEMA)
    result = gen.get_markdown("#SAMPLE__database#")
    assert "| host | string |" in result
    assert "| port | integer |" in result
    assert "| retries | integer, null |" in result


def test_get_markdown_logging_section():
    gen = _make_gen("SAMPLE", SAMPLE_SCHEMA)
    result = gen.get_markdown("#SAMPLE__logging#")
    assert "| level | string |" in result
    assert "| format | string, null |" in result


def test_get_markdown_no_matching_tag_returns_unchanged():
    gen = _make_gen("SAMPLE", SAMPLE_SCHEMA)
    markdown = "Some text with no tags."
    result = gen.get_markdown(markdown)
    assert result == markdown


def test_get_markdown_multiple_tags_in_one_page():
    gen = _make_gen("SAMPLE", SAMPLE_SCHEMA)
    markdown = "DB:\n#SAMPLE__database#\n\nLOG:\n#SAMPLE__logging#"
    result = gen.get_markdown(markdown)
    assert "| host | string |" in result
    assert "| level | string |" in result
