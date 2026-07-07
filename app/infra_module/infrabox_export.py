"""Export helpers for InfraBox JSON / .ibxf backups."""

from __future__ import annotations

from app import store

EXPORTABLE_ENTITIES = store.INFRA_ENTITIES + ['users']


def export_entity(entity: str) -> list:
    return store.get_all(entity)


def export_full_backup() -> dict:
    return {entity: store.get_all(entity) for entity in store.INFRA_ENTITIES}
