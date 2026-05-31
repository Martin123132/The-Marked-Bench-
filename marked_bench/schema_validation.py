from __future__ import annotations

"""Small JSON Schema validator for The Marked Bench public schemas.

The project intentionally uses a narrow, explicit subset of JSON Schema. This
module validates that subset without requiring network access or optional
third-party packages in CI.
"""

import json
import re
from pathlib import Path
from typing import Any, Mapping


def load_json_schema(path: str | Path) -> dict[str, Any]:
    """Load a JSON schema file."""

    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"schema must be a JSON object: {path}")
    return data


def validate_json_schema(
    instance: Any,
    schema: Mapping[str, Any],
    *,
    schema_path: str | Path | None = None,
) -> list[str]:
    """Return schema-conformance errors for a JSON-compatible instance."""

    validator = _SchemaValidator(Path(schema_path).resolve() if schema_path is not None else None)
    return validator.validate(instance, schema)


def validate_json_file(
    instance_path: str | Path,
    schema_path: str | Path,
) -> list[str]:
    """Validate a JSON file against a JSON schema file."""

    instance = json.loads(Path(instance_path).read_text(encoding="utf-8-sig"))
    schema = load_json_schema(schema_path)
    return validate_json_schema(instance, schema, schema_path=schema_path)


class _SchemaValidator:
    def __init__(self, schema_path: Path | None) -> None:
        self.schema_path = schema_path
        self.schema_cache: dict[Path, dict[str, Any]] = {}

    def validate(self, instance: Any, schema: Mapping[str, Any]) -> list[str]:
        return self._validate(instance, schema, path="$", root_schema=schema, schema_path=self.schema_path)

    def _validate(
        self,
        instance: Any,
        schema: Mapping[str, Any],
        *,
        path: str,
        root_schema: Mapping[str, Any],
        schema_path: Path | None,
    ) -> list[str]:
        errors: list[str] = []
        if "$ref" in schema:
            try:
                ref_schema, ref_root, ref_path = self._resolve_ref(str(schema["$ref"]), root_schema, schema_path)
            except ValueError as exc:
                return [f"{path}: {exc}"]
            errors.extend(
                self._validate(instance, ref_schema, path=path, root_schema=ref_root, schema_path=ref_path)
            )

        if "oneOf" in schema:
            options = schema["oneOf"]
            if not isinstance(options, list):
                errors.append(f"{path}: oneOf must be a list")
            else:
                option_errors = [
                    self._validate(instance, option, path=path, root_schema=root_schema, schema_path=schema_path)
                    for option in options
                    if isinstance(option, Mapping)
                ]
                matches = [item for item in option_errors if not item]
                if len(matches) != 1:
                    errors.append(f"{path}: expected exactly one oneOf option to match, got {len(matches)}")

        if "const" in schema and instance != schema["const"]:
            errors.append(f"{path}: expected constant {schema['const']!r}, got {instance!r}")

        if "enum" in schema:
            allowed = schema["enum"]
            if isinstance(allowed, list) and instance not in allowed:
                errors.append(f"{path}: value {instance!r} is not in enum {allowed!r}")

        if "type" in schema:
            expected_types = schema["type"]
            if isinstance(expected_types, str):
                expected_types = [expected_types]
            if not isinstance(expected_types, list) or not any(
                self._matches_type(instance, str(expected)) for expected in expected_types
            ):
                errors.append(f"{path}: expected type {schema['type']!r}, got {self._json_type(instance)!r}")
                return errors

        if isinstance(instance, dict):
            errors.extend(self._validate_object(instance, schema, path, root_schema, schema_path))
        elif isinstance(instance, list):
            errors.extend(self._validate_array(instance, schema, path, root_schema, schema_path))
        elif isinstance(instance, str):
            errors.extend(self._validate_string(instance, schema, path))
        elif isinstance(instance, (int, float)) and not isinstance(instance, bool):
            errors.extend(self._validate_number(instance, schema, path))

        return errors

    def _validate_object(
        self,
        instance: dict[str, Any],
        schema: Mapping[str, Any],
        path: str,
        root_schema: Mapping[str, Any],
        schema_path: Path | None,
    ) -> list[str]:
        errors: list[str] = []
        required = schema.get("required", [])
        if isinstance(required, list):
            for key in required:
                if key not in instance:
                    errors.append(f"{path}: missing required property {key!r}")

        properties = schema.get("properties", {})
        if isinstance(properties, Mapping):
            for key, property_schema in properties.items():
                if key in instance and isinstance(property_schema, Mapping):
                    errors.extend(
                        self._validate(
                            instance[key],
                            property_schema,
                            path=f"{path}.{key}",
                            root_schema=root_schema,
                            schema_path=schema_path,
                        )
                    )

        additional = schema.get("additionalProperties", None)
        known_keys = set(properties) if isinstance(properties, Mapping) else set()
        extra_keys = sorted(set(instance) - known_keys)
        if additional is False and extra_keys:
            errors.append(f"{path}: unexpected properties {extra_keys!r}")
        elif isinstance(additional, Mapping):
            for key in extra_keys:
                errors.extend(
                    self._validate(
                        instance[key],
                        additional,
                        path=f"{path}.{key}",
                        root_schema=root_schema,
                        schema_path=schema_path,
                    )
                )
        return errors

    def _validate_array(
        self,
        instance: list[Any],
        schema: Mapping[str, Any],
        path: str,
        root_schema: Mapping[str, Any],
        schema_path: Path | None,
    ) -> list[str]:
        errors: list[str] = []
        min_items = schema.get("minItems")
        if isinstance(min_items, int) and len(instance) < min_items:
            errors.append(f"{path}: expected at least {min_items} items, got {len(instance)}")
        item_schema = schema.get("items")
        if isinstance(item_schema, Mapping):
            for index, item in enumerate(instance):
                errors.extend(
                    self._validate(
                        item,
                        item_schema,
                        path=f"{path}[{index}]",
                        root_schema=root_schema,
                        schema_path=schema_path,
                    )
                )
        return errors

    def _validate_string(self, instance: str, schema: Mapping[str, Any], path: str) -> list[str]:
        errors: list[str] = []
        min_length = schema.get("minLength")
        if isinstance(min_length, int) and len(instance) < min_length:
            errors.append(f"{path}: expected string length at least {min_length}, got {len(instance)}")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and not re.search(pattern, instance):
            errors.append(f"{path}: string does not match pattern {pattern!r}")
        return errors

    def _validate_number(self, instance: int | float, schema: Mapping[str, Any], path: str) -> list[str]:
        errors: list[str] = []
        minimum = schema.get("minimum")
        if isinstance(minimum, (int, float)) and instance < minimum:
            errors.append(f"{path}: expected value >= {minimum}, got {instance}")
        maximum = schema.get("maximum")
        if isinstance(maximum, (int, float)) and instance > maximum:
            errors.append(f"{path}: expected value <= {maximum}, got {instance}")
        return errors

    def _resolve_ref(
        self,
        ref: str,
        root_schema: Mapping[str, Any],
        schema_path: Path | None,
    ) -> tuple[Mapping[str, Any], Mapping[str, Any], Path | None]:
        if "#" in ref:
            target_path, pointer = ref.split("#", 1)
        else:
            target_path, pointer = ref, ""

        if target_path:
            if schema_path is None:
                raise ValueError(f"cannot resolve external ref without schema path: {ref}")
            ref_path = (schema_path.parent / target_path).resolve()
            ref_root = self._load_cached_schema(ref_path)
        else:
            ref_path = schema_path
            ref_root = root_schema

        ref_schema: Any = ref_root
        if pointer:
            ref_schema = self._resolve_pointer(ref_root, pointer)
        if not isinstance(ref_schema, Mapping):
            raise ValueError(f"ref does not resolve to a schema object: {ref}")
        return ref_schema, ref_root, ref_path

    def _load_cached_schema(self, path: Path) -> dict[str, Any]:
        if path not in self.schema_cache:
            self.schema_cache[path] = load_json_schema(path)
        return self.schema_cache[path]

    @staticmethod
    def _resolve_pointer(document: Mapping[str, Any], pointer: str) -> Any:
        if not pointer:
            return document
        if not pointer.startswith("/"):
            raise ValueError(f"unsupported JSON pointer: #{pointer}")
        current: Any = document
        for raw_part in pointer.lstrip("/").split("/"):
            part = raw_part.replace("~1", "/").replace("~0", "~")
            if isinstance(current, Mapping) and part in current:
                current = current[part]
            else:
                raise ValueError(f"unresolvable JSON pointer: #{pointer}")
        return current

    @staticmethod
    def _matches_type(value: Any, expected: str) -> bool:
        if expected == "object":
            return isinstance(value, dict)
        if expected == "array":
            return isinstance(value, list)
        if expected == "string":
            return isinstance(value, str)
        if expected == "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        if expected == "number":
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        if expected == "boolean":
            return isinstance(value, bool)
        if expected == "null":
            return value is None
        return False

    @staticmethod
    def _json_type(value: Any) -> str:
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, dict):
            return "object"
        if isinstance(value, list):
            return "array"
        if isinstance(value, str):
            return "string"
        if isinstance(value, int):
            return "integer"
        if isinstance(value, float):
            return "number"
        return type(value).__name__


__all__ = [
    "load_json_schema",
    "validate_json_file",
    "validate_json_schema",
]
