"""Import helpers for NetBox CSV exports."""

from __future__ import annotations

import csv
import io

from app.infra_module.models import TagM, ProgramM, ProductM, ServerM, ServerRoleM, ServerLocationM
from app.infra_module.other import SERVER_STATUS_CHOICES

_STATUS_LABEL_TO_SLUG = {label.lower(): slug for slug, label in SERVER_STATUS_CHOICES}
_STATUS_LABEL_TO_SLUG.update({slug: slug for slug, _ in SERVER_STATUS_CHOICES})
_STATUS_LABEL_TO_SLUG['inventory'] = 'staged'


def _read_csv_rows(file_stream) -> csv.DictReader:
    raw = file_stream.read()
    if isinstance(raw, bytes):
        raw = raw.decode('utf-8-sig')
    return csv.DictReader(io.StringIO(raw))


def _normalize_color(value: str) -> str:
    color = (value or '6c757d').strip().lstrip('#')
    if len(color) > 6:
        color = color[:6]
    return color or '6c757d'


def _normalize_status(value: str) -> str:
    key = (value or 'active').strip().lower()
    return _STATUS_LABEL_TO_SLUG.get(key, 'active')


def _parse_device_names(cell: str) -> list[str]:
    """Split NetBox cell on newlines and commas; strip whitespace; drop empties."""
    if not cell:
        return []
    names = []
    for part in cell.replace(',', '\n').split('\n'):
        name = part.strip()
        if name:
            names.append(name)
    return names


def _resolve_name_ids(cell: str, finder, row_num: int, field: str,
                      errors: list[str]) -> list[int]:
    """Resolve comma/newline-separated names to entity IDs; log missing refs."""
    ids = []
    seen = set()
    for name in _parse_device_names(cell):
        obj = finder(name)
        if obj:
            oid = int(obj['id'])
            if oid not in seen:
                ids.append(oid)
                seen.add(oid)
        else:
            errors.append(f'Row {row_num}: {field} "{name}" not found')
    return ids


def _resolve_location_id(cell: str, finder, row_num: int, errors: list[str]) -> int | None:
    name = (cell or '').strip()
    if not name:
        return None
    obj = finder(name)
    if obj:
        return int(obj['id'])
    errors.append(f'Row {row_num}: Server Location "{name}" not found')
    return None


def import_tags_csv(file_stream) -> dict:
    """
    Import tags from a NetBox tag export CSV.

    Expected columns: Name, Color, Description (others are ignored).
    Skips tags whose name already exists (case-insensitive).
    """
    reader = _read_csv_rows(file_stream)
    added = 0
    skipped = 0
    errors: list[str] = []

    for row_num, row in enumerate(reader, start=2):
        name = (row.get('Name') or '').strip()
        if not name:
            errors.append(f'Row {row_num}: missing Name')
            continue

        if TagM.find_by_name(name):
            skipped += 1
            continue

        color = _normalize_color(row.get('Color', ''))
        comments = (row.get('Description') or '').strip()

        TagM.create(name=name, color=color, comments=comments)
        added += 1

    return {'added': added, 'skipped': skipped, 'errors': errors}


def import_server_roles_csv(file_stream) -> dict:
    """
    Import server roles from a NetBox device role export CSV.

    Uses Name -> name, Color -> color, Description -> description.
    Other columns (Devices count, VMs, Slug, ID, etc.) are ignored.
    Skips roles whose name already exists (case-insensitive).
    """
    reader = _read_csv_rows(file_stream)
    added = 0
    skipped = 0
    errors: list[str] = []

    for row_num, row in enumerate(reader, start=2):
        name = (row.get('Name') or '').strip()
        if not name:
            errors.append(f'Row {row_num}: missing Name')
            continue

        if ServerRoleM.find_by_name(name):
            skipped += 1
            continue

        color = _normalize_color(row.get('Color', ''))
        description = (row.get('Description') or '').strip()

        ServerRoleM.create(name=name, color=color, description=description)
        added += 1

    return {'added': added, 'skipped': skipped, 'errors': errors}


def import_products_csv(file_stream) -> dict:
    """
    Import products from a NetBox product export CSV.

    Uses Name -> name, Comments -> comments.
    Devices column: link product to servers whose name matches (case-insensitive).
    Skips creating products whose name already exists, but still applies device links.
    """
    reader = _read_csv_rows(file_stream)
    added = 0
    skipped = 0
    links_created = 0
    links_missing = 0
    errors: list[str] = []

    for row_num, row in enumerate(reader, start=2):
        name = (row.get('Name') or '').strip()
        if not name:
            errors.append(f'Row {row_num}: missing Name')
            continue

        comments = (row.get('Comments') or '').strip()
        existing = ProductM.find_by_name(name)
        if existing:
            product_id = existing['id']
            skipped += 1
        else:
            product_id = ProductM.create(name=name, comments=comments)
            added += 1

        for device_name in _parse_device_names(row.get('Devices', '')):
            server = ServerM.find_by_name(device_name)
            if server:
                if ServerM.link_product(server['id'], product_id):
                    links_created += 1
            else:
                links_missing += 1

    return {
        'added': added,
        'skipped': skipped,
        'links_created': links_created,
        'links_missing': links_missing,
        'errors': errors,
    }


def import_programs_csv(file_stream) -> dict:
    """
    Import programs from a NetBox program export CSV.

    Uses Name -> name, Comments -> comments.
    Devices column: link program to servers whose name matches (case-insensitive).
    Skips creating programs whose name already exists, but still applies device links.
    """
    reader = _read_csv_rows(file_stream)
    added = 0
    skipped = 0
    links_created = 0
    links_missing = 0
    errors: list[str] = []

    for row_num, row in enumerate(reader, start=2):
        name = (row.get('Name') or '').strip()
        if not name:
            errors.append(f'Row {row_num}: missing Name')
            continue

        comments = (row.get('Comments') or '').strip()
        existing = ProgramM.find_by_name(name)
        if existing:
            program_id = existing['id']
            skipped += 1
        else:
            program_id = ProgramM.create(name=name, comments=comments)
            added += 1

        for device_name in _parse_device_names(row.get('Devices', '')):
            server = ServerM.find_by_name(device_name)
            if server:
                if ServerM.link_program(server['id'], program_id):
                    links_created += 1
            else:
                links_missing += 1

    return {
        'added': added,
        'skipped': skipped,
        'links_created': links_created,
        'links_missing': links_missing,
        'errors': errors,
    }


def import_servers_csv(file_stream) -> dict:
    """
    Import servers from a NetBox device export CSV.

    Maps scalar fields and resolves Roles, Products, Programs, Tags by name.
    Skips servers whose name already exists (case-insensitive).
    Missing role/product/program/tag names are reported but the server is still created.
    """
    reader = _read_csv_rows(file_stream)
    added = 0
    skipped = 0
    errors: list[str] = []

    for row_num, row in enumerate(reader, start=2):
        name = (row.get('Name') or '').strip()
        if not name:
            errors.append(f'Row {row_num}: missing Name')
            continue

        if ServerM.find_by_name(name):
            skipped += 1
            continue

        role_ids = _resolve_name_ids(
            row.get('Roles', ''), ServerRoleM.find_by_name, row_num, 'Role', errors,
        )
        product_ids = _resolve_name_ids(
            row.get('Products', ''), ProductM.find_by_name, row_num, 'Product', errors,
        )
        program_ids = _resolve_name_ids(
            row.get('Programs', ''), ProgramM.find_by_name, row_num, 'Program', errors,
        )
        tag_ids = _resolve_name_ids(
            row.get('Tags', ''), TagM.find_by_name, row_num, 'Tag', errors,
        )
        location_id = _resolve_location_id(
            row.get('Server Location', ''), ServerLocationM.find_by_name, row_num, errors,
        )

        ServerM.create(
            name=name,
            role_ids=role_ids,
            ip_address=(row.get('IP Address') or '').strip(),
            url=(row.get('URL') or '').strip(),
            os_=(row.get('OS') or '').strip(),
            comments=(row.get('Comments') or '').strip(),
            status=_normalize_status(row.get('Status', '')),
            product_ids=product_ids,
            program_ids=program_ids,
            tag_ids=tag_ids,
            cpu=(row.get('CPU') or '').strip(),
            cpu_cores=(row.get('CPU Cores') or '').strip(),
            ram=(row.get('RAM') or '').strip(),
            disk=(row.get('DISK') or '').strip(),
            location_id=location_id,
        )
        added += 1

    return {'added': added, 'skipped': skipped, 'errors': errors}
