"""Import helpers for InfraBox JSON / .ibxf backups."""

from __future__ import annotations

import json

from app import store

IMPORT_ORDER = store.INFRA_ENTITIES


class InfraBoxImportError(Exception):
    pass


def _load_json(file_stream) -> object:
    raw = file_stream.read()
    if isinstance(raw, bytes):
        raw = raw.decode('utf-8-sig')
    try:
        return json.loads(raw)
    except json.JSONDecodeError as err:
        raise InfraBoxImportError(f'Invalid JSON: {err}') from err


def _validate_entity_list(entity: str, data: object) -> list:
    if not isinstance(data, list):
        raise InfraBoxImportError(f'Expected a JSON array for {entity}.')
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise InfraBoxImportError(f'{entity}[{i}]: expected an object.')
        if 'id' not in item:
            raise InfraBoxImportError(f'{entity}[{i}]: missing id.')
    return data


def import_entity_json(entity: str, file_stream) -> int:
    """Replace all records for one entity from a JSON array file."""
    if entity not in store.ENTITIES:
        raise InfraBoxImportError(f'Unknown entity: {entity}.')
    data = _load_json(file_stream)
    items = _validate_entity_list(entity, data)
    store.replace_all(entity, items)
    return len(items)


def import_full_backup(file_stream) -> dict[str, int]:
    """
    Replace all infra entities from a full .ibxf backup.
    On failure, restores a pre-import in-memory snapshot.
    """
    snap = store.snapshot(IMPORT_ORDER)
    try:
        data = _load_json(file_stream)
        if not isinstance(data, dict):
            raise InfraBoxImportError('Full backup must be a JSON object.')

        for entity in IMPORT_ORDER:
            if entity not in data:
                raise InfraBoxImportError(f'Missing key: {entity}.')
            _validate_entity_list(entity, data[entity])

        counts = {}
        for entity in IMPORT_ORDER:
            store.replace_all(entity, data[entity])
            counts[entity] = len(data[entity])
        return counts
    except Exception:
        store.restore_snapshot(snap)
        raise
