#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / ".ai/schemas/cycle.schema.json"
TELEMETRY_PATH = ROOT / ".ai/telemetry/cycles.jsonl"


def load_schema(path: Path = SCHEMA_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _matches_type(value: Any, expected: str) -> bool:
    if expected == "null":
        return value is None
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    return True


def _valid_datetime(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def validate_row(row: dict[str, Any], schema: dict[str, Any] | None = None) -> list[str]:
    schema = schema or load_schema()
    errors: list[str] = []

    for key in schema.get("required", []):
        if key not in row:
            errors.append(f"missing required field: {key}")

    props = schema.get("properties", {})
    if schema.get("additionalProperties") is False:
        for key in row:
            if key not in props:
                errors.append(f"unexpected field: {key}")

    for key, value in row.items():
        spec = props.get(key)
        if not spec:
            continue

        expected = spec.get("type")
        if expected is not None:
            expected_types = expected if isinstance(expected, list) else [expected]
            if not any(_matches_type(value, t) for t in expected_types):
                errors.append(f"{key}: invalid type")
                continue

        if "enum" in spec and value not in spec["enum"]:
            errors.append(f"{key}: value {value!r} is not allowed")

        minimum = spec.get("minimum")
        if minimum is not None and value is not None and isinstance(value, (int, float)):
            if value < minimum:
                errors.append(f"{key}: must be >= {minimum}")

        if spec.get("format") == "date-time" and isinstance(value, str):
            if not _valid_datetime(value):
                errors.append(f"{key}: invalid ISO-8601 date-time")

    if isinstance(row.get("started_at"), str) and isinstance(row.get("ended_at"), str):
        try:
            a = datetime.fromisoformat(row["started_at"].replace("Z", "+00:00"))
            b = datetime.fromisoformat(row["ended_at"].replace("Z", "+00:00"))
            if b < a:
                errors.append("ended_at must be >= started_at")
        except ValueError:
            pass

    return errors


def load_jsonl(path: Path = TELEMETRY_PATH, validate: bool = True) -> list[dict[str, Any]]:
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        return []

    schema = load_schema()
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}: invalid JSON on line {line_no}: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path}: line {line_no} must be a JSON object")
        if validate:
            errors = validate_row(row, schema)
            if errors:
                raise ValueError(f"{path}: line {line_no}: " + "; ".join(errors))
        rows.append(row)
    return rows
