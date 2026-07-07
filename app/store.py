"""
JSON-backed in-memory store.

All data lives in DATA_DIR/*.json files and is loaded into module-level
lists at startup. Reads are done entirely in-memory. Writes update memory
first, then flush atomically to disk (write temp → rename).

Single-worker gunicorn is assumed, so a simple threading.Lock is enough.
"""
from __future__ import annotations

import json
import os
import shutil
import threading
from datetime import date

_store = {}  # type: dict[str, list]
_os_index: list[dict] = []  # [{name, count}, ...] — rebuilt when servers change
_lock = threading.Lock()

ENTITIES = ['users', 'server_roles', 'server_locations', 'servers', 'products', 'programs', 'tags']

INFRA_ENTITIES = ['tags', 'server_roles', 'products', 'programs', 'server_locations', 'servers']

_DATA_DIR = 'data'


def configure(data_dir: str):
    global _DATA_DIR
    _DATA_DIR = data_dir


def _file(entity: str) -> str:
    return os.path.join(_DATA_DIR, f'{entity}.json')


def _rebuild_os_index():
    """Build distinct OS list from in-memory servers (case-insensitive, most common spelling)."""
    global _os_index
    groups: dict[str, dict[str, int]] = {}
    for s in _store.get('servers', []):
        os_val = (s.get('os') or '').strip()
        if not os_val:
            continue
        key = os_val.lower()
        variants = groups.setdefault(key, {})
        variants[os_val] = variants.get(os_val, 0) + 1

    result = []
    for variants in groups.values():
        name = max(variants.items(), key=lambda x: (x[1], x[0].lower()))[0]
        result.append({'name': name, 'count': sum(variants.values())})
    result.sort(key=lambda x: (-x['count'], x['name'].lower()))
    _os_index = result


def _maybe_rebuild_os_index(entity: str):
    if entity == 'servers':
        _rebuild_os_index()


def get_distinct_os_values() -> list:
    """Return cached distinct OS values. Rebuilt when server data changes."""
    return list(_os_index)


def load_all():
    """Load all JSON files into memory. Called once at app startup."""
    os.makedirs(_DATA_DIR, exist_ok=True)
    for entity in ENTITIES:
        path = _file(entity)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                try:
                    _store[entity] = json.load(f)
                except json.JSONDecodeError:
                    _store[entity] = []
        else:
            _store[entity] = []
            _flush(entity)
    _rebuild_os_index()


def _flush(entity: str):
    """Write entity list to disk atomically."""
    path = _file(entity)
    tmp = path + '.tmp'
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(_store[entity], f, indent=2, ensure_ascii=False, default=str)
    shutil.move(tmp, path)


def get_all(entity: str) -> list:
    return list(_store.get(entity, []))


def get_one(entity: str, id_) -> dict | None:
    id_ = int(id_)
    for item in _store.get(entity, []):
        if item.get('id') == id_:
            return dict(item)
    return None


def _next_id(entity: str) -> int:
    items = _store.get(entity, [])
    if not items:
        return 1
    return max(item['id'] for item in items) + 1


def create(entity: str, data: dict) -> int:
    with _lock:
        data = dict(data)
        data['id'] = _next_id(entity)
        if entity not in ('users',):
            today = date.today().isoformat()
            data.setdefault('created', today)
            data.setdefault('updated', today)
        _store.setdefault(entity, []).append(data)
        _flush(entity)
        _maybe_rebuild_os_index(entity)
        return data['id']


def update(entity: str, id_, data: dict) -> bool:
    with _lock:
        id_ = int(id_)
        items = _store.get(entity, [])
        for i, item in enumerate(items):
            if item.get('id') == id_:
                updated = dict(item)
                updated.update(data)
                updated['id'] = id_
                if entity not in ('users',):
                    updated['updated'] = date.today().isoformat()
                items[i] = updated
                _store[entity] = items
                _flush(entity)
                _maybe_rebuild_os_index(entity)
                return True
        return False


def delete(entity: str, id_) -> bool:
    with _lock:
        id_ = int(id_)
        items = _store.get(entity, [])
        new_items = [item for item in items if item.get('id') != id_]
        if len(new_items) == len(items):
            return False
        _store[entity] = new_items
        _flush(entity)
        _maybe_rebuild_os_index(entity)
        return True


def replace_all(entity: str, items: list) -> None:
    """Replace an entire entity list in memory and on disk. Preserves IDs from items."""
    with _lock:
        _store[entity] = [dict(item) for item in items]
        _flush(entity)
        _maybe_rebuild_os_index(entity)


def snapshot(entities: list[str]) -> dict[str, list]:
    """Deep-copy current in-memory lists for rollback."""
    return {entity: [dict(item) for item in _store.get(entity, [])] for entity in entities}


def restore_snapshot(snap: dict[str, list]) -> None:
    """Restore entities from a snapshot (memory + disk)."""
    with _lock:
        servers_changed = False
        for entity, items in snap.items():
            _store[entity] = [dict(item) for item in items]
            _flush(entity)
            if entity == 'servers':
                servers_changed = True
        if servers_changed:
            _rebuild_os_index()
