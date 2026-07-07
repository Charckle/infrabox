from datetime import date

from flask import Blueprint, render_template, flash, redirect, url_for, jsonify, abort

from app.infra_module.forms import (
    NetboxTagsImportForm,
    NetboxProductsImportForm,
    NetboxProgramsImportForm,
    NetboxServerRolesImportForm,
    NetboxServersImportForm,
    InfraBoxFullBackupImportForm,
    InfraBoxTagsImportForm,
    InfraBoxServerRolesImportForm,
    InfraBoxProductsImportForm,
    InfraBoxProgramsImportForm,
    InfraBoxServerLocationsImportForm,
    InfraBoxServersImportForm,
    InfraBoxUsersImportForm,
)
from app.infra_module.netbox_import import (
    import_tags_csv,
    import_products_csv,
    import_programs_csv,
    import_server_roles_csv,
    import_servers_csv,
)
from app.infra_module.infrabox_export import export_entity, export_full_backup, EXPORTABLE_ENTITIES
from app.infra_module.infrabox_import import import_entity_json, import_full_backup, InfraBoxImportError
from app.infra_module.other import UserRole
from app.wrappers import access_required

import_export_module = Blueprint('import_export_module', __name__, url_prefix='/import-export')

ENTITY_LABELS = {
    'tags': 'Tags',
    'server_roles': 'Server roles',
    'products': 'Products',
    'programs': 'Programs',
    'server_locations': 'Server locations',
    'servers': 'Servers',
    'users': 'Users',
}


def _flash_netbox_import_result(label: str, result: dict, extra_keys: tuple = ()):
    parts = [f'{result["added"]} added', f'{result["skipped"]} skipped']
    for key in extra_keys:
        if key in result:
            parts.append(f'{result[key]} {key.replace("_", " ")}')
    msg = f'{label}: {", ".join(parts)}.'
    if result.get('errors'):
        msg += f' {len(result["errors"])} row(s) had errors.'
        flash(msg, 'error')
        for err in result['errors'][:5]:
            flash(err, 'error')
        if len(result['errors']) > 5:
            flash(f'…and {len(result["errors"]) - 5} more errors.', 'error')
    else:
        flash(msg, 'success')


def _flash_infrabox_entity_import(label: str, count: int):
    flash(f'{label}: replaced with {count} record(s).', 'success')


def _flash_infrabox_import_error(err: InfraBoxImportError):
    flash(str(err), 'error')


def _json_download(data, filename: str):
    response = jsonify(data)
    response.mimetype = 'application/json'
    response.headers['Content-Disposition'] = f'attachment;filename={filename}'
    return response


@import_export_module.route('/', methods=['GET'])
@access_required(UserRole.ADMIN)
def import_export_index():
    return render_template('infra_module/import_export/index.html')


@import_export_module.route('/netbox/', methods=['GET', 'POST'])
@access_required(UserRole.ADMIN)
def netbox_import():
    tags_form = NetboxTagsImportForm(prefix='tags')
    roles_form = NetboxServerRolesImportForm(prefix='roles')
    products_form = NetboxProductsImportForm(prefix='products')
    programs_form = NetboxProgramsImportForm(prefix='programs')
    servers_form = NetboxServersImportForm(prefix='servers')

    if tags_form.validate_on_submit():
        result = import_tags_csv(tags_form.import_file.data)
        _flash_netbox_import_result('Tags', result)
        return redirect(url_for('import_export_module.netbox_import'))

    if roles_form.validate_on_submit():
        result = import_server_roles_csv(roles_form.import_file.data)
        _flash_netbox_import_result('Server roles', result)
        return redirect(url_for('import_export_module.netbox_import'))

    if products_form.validate_on_submit():
        result = import_products_csv(products_form.import_file.data)
        _flash_netbox_import_result(
            'Products', result,
            extra_keys=('links_created', 'links_missing'),
        )
        return redirect(url_for('import_export_module.netbox_import'))

    if programs_form.validate_on_submit():
        result = import_programs_csv(programs_form.import_file.data)
        _flash_netbox_import_result(
            'Programs', result,
            extra_keys=('links_created', 'links_missing'),
        )
        return redirect(url_for('import_export_module.netbox_import'))

    if servers_form.validate_on_submit():
        result = import_servers_csv(servers_form.import_file.data)
        _flash_netbox_import_result('Servers', result)
        return redirect(url_for('import_export_module.netbox_import'))

    for form in (tags_form, roles_form, products_form, programs_form, servers_form):
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')

    return render_template(
        'infra_module/import_export/netbox.html',
        tags_form=tags_form,
        roles_form=roles_form,
        products_form=products_form,
        programs_form=programs_form,
        servers_form=servers_form,
    )


@import_export_module.route('/infrabox/export/', methods=['GET'])
@access_required(UserRole.ADMIN)
def infrabox_export():
    return render_template('infra_module/import_export/infrabox_export.html')


@import_export_module.route('/infrabox/export/full/', methods=['GET'])
@access_required(UserRole.ADMIN)
def infrabox_export_full():
    data = export_full_backup()
    filename = f'infrabox-backup-{date.today().isoformat()}.ibxf'
    return _json_download(data, filename)


@import_export_module.route('/infrabox/export/<entity>/', methods=['GET'])
@access_required(UserRole.ADMIN)
def infrabox_export_entity(entity):
    if entity not in EXPORTABLE_ENTITIES:
        abort(404)
    data = export_entity(entity)
    return _json_download(data, f'{entity}.json')


@import_export_module.route('/infrabox/import/', methods=['GET', 'POST'])
@access_required(UserRole.ADMIN)
def infrabox_import():
    full_form = InfraBoxFullBackupImportForm(prefix='full')
    tags_form = InfraBoxTagsImportForm(prefix='tags')
    roles_form = InfraBoxServerRolesImportForm(prefix='roles')
    products_form = InfraBoxProductsImportForm(prefix='products')
    programs_form = InfraBoxProgramsImportForm(prefix='programs')
    locations_form = InfraBoxServerLocationsImportForm(prefix='locations')
    servers_form = InfraBoxServersImportForm(prefix='servers')
    users_form = InfraBoxUsersImportForm(prefix='users')

    if full_form.validate_on_submit():
        try:
            counts = import_full_backup(full_form.import_file.data)
            parts = [f'{ENTITY_LABELS[e]}: {counts[e]}' for e in counts]
            flash(f'Full backup imported — {", ".join(parts)}.', 'success')
        except InfraBoxImportError as err:
            _flash_infrabox_import_error(err)
        except Exception as err:
            flash(f'Import failed and data was restored: {err}', 'error')
        return redirect(url_for('import_export_module.infrabox_import'))

    entity_forms = [
        ('tags', tags_form),
        ('server_roles', roles_form),
        ('products', products_form),
        ('programs', programs_form),
        ('server_locations', locations_form),
        ('servers', servers_form),
        ('users', users_form),
    ]

    for entity, form in entity_forms:
        if form.validate_on_submit():
            try:
                count = import_entity_json(entity, form.import_file.data)
                _flash_infrabox_entity_import(ENTITY_LABELS[entity], count)
            except InfraBoxImportError as err:
                _flash_infrabox_import_error(err)
            except Exception as err:
                flash(f'Import failed: {err}', 'error')
            return redirect(url_for('import_export_module.infrabox_import'))

    for form in (full_form, tags_form, roles_form, products_form,
                 programs_form, locations_form, servers_form, users_form):
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')

    return render_template(
        'infra_module/import_export/infrabox_import.html',
        full_form=full_form,
        tags_form=tags_form,
        roles_form=roles_form,
        products_form=products_form,
        programs_form=programs_form,
        locations_form=locations_form,
        servers_form=servers_form,
        users_form=users_form,
    )
