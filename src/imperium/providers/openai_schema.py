"""Reversible adaptation from Pydantic JSON Schema to OpenAI Structured Outputs.

OpenAI supports a strict subset of JSON Schema. In particular, object fields must
be required, objects must reject additional properties, arbitrary-key maps cannot
be represented directly, and generated regular-expression constraints may use
unsupported syntax. This module converts maps into arrays of ``{"key": ...,
"value": ...}`` entries for the wire format, removes constraints that remain
authoritative in final Pydantic validation, and restores maps before domain-model
validation.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


class StructuredSchemaError(ValueError):
    """Raised when adapted structured output cannot be restored safely."""


# Keep only constraints known to be accepted by the Structured Outputs boundary.
# Pydantic remains the authoritative validator after the wire payload is decoded.
# ``pattern`` is deliberately excluded because Pydantic's Decimal schema contains
# regex lookaround, which the Codex/OpenAI schema compiler rejects.
_SCALAR_KEYS = {
    "type",
    "description",
    "enum",
    "format",
    "multipleOf",
    "maximum",
    "exclusiveMaximum",
    "minimum",
    "exclusiveMinimum",
    "minItems",
    "maxItems",
}


def _is_dynamic_map(schema: Mapping[str, Any]) -> bool:
    properties = schema.get("properties")
    return (
        schema.get("type") == "object"
        and isinstance(schema.get("additionalProperties"), Mapping)
        and not properties
    )


def _adapt_key_schema(schema: object) -> dict[str, Any]:
    adapted: dict[str, Any] = {"type": "string"}
    if isinstance(schema, Mapping):
        for key in ("description", "format"):
            value = schema.get(key)
            if value is not None:
                adapted[key] = deepcopy(value)
    return adapted


def _adapt_node(schema: Mapping[str, Any]) -> dict[str, Any]:
    if "$ref" in schema:
        return {"$ref": schema["$ref"]}

    if _is_dynamic_map(schema):
        value_schema = schema["additionalProperties"]
        assert isinstance(value_schema, Mapping)
        description = schema.get("description")
        wire_description = (
            f"{description} " if isinstance(description, str) and description else ""
        ) + "Represent this mapping as an array of unique key/value entries."
        return {
            "type": "array",
            "description": wire_description,
            "items": {
                "type": "object",
                "properties": {
                    "key": _adapt_key_schema(schema.get("propertyNames")),
                    "value": _adapt_node(value_schema),
                },
                "required": ["key", "value"],
                "additionalProperties": False,
            },
        }

    adapted: dict[str, Any] = {}
    for key in _SCALAR_KEYS:
        if key in schema:
            adapted[key] = deepcopy(schema[key])

    if "const" in schema:
        adapted["enum"] = [deepcopy(schema["const"])]

    any_of = schema.get("anyOf")
    if isinstance(any_of, list):
        adapted["anyOf"] = [
            _adapt_node(option) for option in any_of if isinstance(option, Mapping)
        ]

    definitions = schema.get("$defs")
    if isinstance(definitions, Mapping):
        adapted["$defs"] = {
            str(name): _adapt_node(definition)
            for name, definition in definitions.items()
            if isinstance(definition, Mapping)
        }

    properties = schema.get("properties")
    if isinstance(properties, Mapping):
        adapted_properties = {
            str(name): _adapt_node(property_schema)
            for name, property_schema in properties.items()
            if isinstance(property_schema, Mapping)
        }
        adapted["type"] = "object"
        adapted["properties"] = adapted_properties
        adapted["required"] = list(adapted_properties)
        adapted["additionalProperties"] = False

    items = schema.get("items")
    if isinstance(items, Mapping):
        adapted["items"] = _adapt_node(items)

    return adapted


def adapt_pydantic_schema(schema: Mapping[str, Any]) -> dict[str, Any]:
    """Return an OpenAI-compatible wire schema without mutating ``schema``."""

    return _adapt_node(deepcopy(schema))


def _resolve_ref(schema: Mapping[str, Any], root: Mapping[str, Any]) -> Mapping[str, Any]:
    reference = schema.get("$ref")
    if not isinstance(reference, str):
        return schema
    prefix = "#/$defs/"
    if not reference.startswith(prefix):
        raise StructuredSchemaError(f"unsupported JSON Schema reference: {reference!r}")
    name = reference[len(prefix) :]
    definitions = root.get("$defs")
    if not isinstance(definitions, Mapping) or not isinstance(definitions.get(name), Mapping):
        raise StructuredSchemaError(f"unresolved JSON Schema reference: {reference!r}")
    return definitions[name]


def _decode_node(value: Any, schema: Mapping[str, Any], root: Mapping[str, Any]) -> Any:
    schema = _resolve_ref(schema, root)

    if _is_dynamic_map(schema):
        if not isinstance(value, list):
            raise StructuredSchemaError("structured map output must be an array of entries")
        value_schema = schema["additionalProperties"]
        assert isinstance(value_schema, Mapping)
        restored: dict[str, Any] = {}
        for entry in value:
            if not isinstance(entry, Mapping) or set(entry) != {"key", "value"}:
                raise StructuredSchemaError(
                    "structured map entries must contain exactly 'key' and 'value'"
                )
            key = entry["key"]
            if not isinstance(key, str):
                raise StructuredSchemaError("structured map keys must be strings")
            if key in restored:
                raise StructuredSchemaError(f"duplicate structured map key: {key!r}")
            restored[key] = _decode_node(entry["value"], value_schema, root)
        return restored

    properties = schema.get("properties")
    if isinstance(value, Mapping) and isinstance(properties, Mapping):
        restored_object = dict(value)
        for name, property_schema in properties.items():
            if name in restored_object and isinstance(property_schema, Mapping):
                restored_object[name] = _decode_node(
                    restored_object[name], property_schema, root
                )
        return restored_object

    items = schema.get("items")
    if isinstance(value, list) and isinstance(items, Mapping):
        return [_decode_node(item, items, root) for item in value]

    any_of = schema.get("anyOf")
    if isinstance(any_of, list):
        for option in any_of:
            if not isinstance(option, Mapping):
                continue
            resolved = _resolve_ref(option, root)
            if _is_dynamic_map(resolved) and isinstance(value, list):
                return _decode_node(value, resolved, root)
            if resolved.get("type") == "object" and isinstance(value, Mapping):
                return _decode_node(value, resolved, root)
            if resolved.get("type") == "array" and isinstance(value, list):
                return _decode_node(value, resolved, root)

    return value


def restore_pydantic_payload(value: Any, original_schema: Mapping[str, Any]) -> Any:
    """Restore adapted map representations to their domain JSON shape."""

    return _decode_node(value, original_schema, original_schema)
