from flask import (Blueprint, request, render_template, flash,
                   redirect, url_for)

from app.infra_module.forms import ServerForm
from app.infra_module.models import ServerM, ServerRoleM, ProductM, ProgramM, TagM, ServerLocationM
from app.infra_module.other import UserRole, SERVER_STATUS_CHOICES
from app.wrappers import access_required

servers_module = Blueprint('servers_module', __name__, url_prefix='/servers')


def _populate_choices(form):
    form.role_ids.choices = [(r['id'], r['name']) for r in ServerRoleM.get_all()]
    form.product_ids.choices = [(p['id'], p['name']) for p in ProductM.get_all()]
    form.program_ids.choices = [(p['id'], p['name']) for p in ProgramM.get_all()]
    form.tag_ids.choices = [(t['id'], t['name']) for t in TagM.get_all()]
    form.location_id.choices = [('', '—')] + [
        (loc['id'], loc['name']) for loc in ServerLocationM.get_all()
    ]


def _prefill_form_from_server(form, server, *, name=None, include_ip_url=True):
    form.name.data = name if name is not None else server['name']
    form.status.data = server.get('status', 'active')
    form.ip_address.data = server.get('ip_address', '') if include_ip_url else ''
    form.url.data = server.get('url', '') if include_ip_url else ''
    form.os.data = server.get('os', '')
    form.cpu.data = server.get('cpu', '')
    form.cpu_cores.data = server.get('cpu_cores', '')
    form.ram.data = server.get('ram', '')
    form.disk.data = server.get('disk', '')
    form.location_id.data = server.get('location_id') or None
    form.comments.data = server.get('comments', '')
    form.role_ids.data = [int(r) for r in server.get('role_ids', [])]
    form.product_ids.data = [int(p) for p in server.get('product_ids', [])]
    form.program_ids.data = [int(p) for p in server.get('program_ids', [])]
    form.tag_ids.data = [int(t) for t in server.get('tag_ids', [])]


def _parse_id_list(values) -> list[int]:
    ids = []
    for v in values:
        v = (v or '').strip()
        if v.isdigit():
            ids.append(int(v))
    return ids


def _filters_active(filters: dict) -> bool:
    for key, value in filters.items():
        if key == 'product_ids':
            if value:
                return True
        elif value:
            return True
    return False


@servers_module.route('/', methods=['GET'])
@access_required()
def servers_all():
    init_filters = {
        'q':            request.args.get('q', '').strip(),
        'statuses':     [s.strip() for s in request.args.getlist('status') if s.strip()],
        'role_ids':     _parse_id_list(request.args.getlist('role_id')),
        'product_ids':  _parse_id_list(request.args.getlist('product_id')),
        'program_ids':  _parse_id_list(request.args.getlist('program_id')),
        'location_ids': _parse_id_list(request.args.getlist('location_id')),
        'tag_ids':      _parse_id_list(request.args.getlist('tag_id')),
    }
    servers = sorted(ServerM.get_all(), key=lambda s: (s.get('name') or '').casefold())
    roles = ServerRoleM.get_all()
    products = ProductM.get_all()
    programs = ProgramM.get_all()
    locations = ServerLocationM.get_all()
    tags = TagM.get_all()

    return render_template(
        'infra_module/servers/servers_all.html',
        servers=servers,
        roles=roles,
        products=products,
        programs=programs,
        locations=locations,
        tags=tags,
        statuses=SERVER_STATUS_CHOICES,
        init_filters=init_filters,
    )


@servers_module.route('/<int:server_id>/', methods=['GET'])
@access_required()
def server_view(server_id):
    server = ServerM.get_one(server_id)
    if not server:
        flash('Server not found.', 'error')
        return redirect(url_for('servers_module.servers_all'))

    server_roles = ServerRoleM.get_by_ids(server.get('role_ids', []))
    server_products = ProductM.get_by_ids(server.get('product_ids', []))
    server_programs = ProgramM.get_by_ids(server.get('program_ids', []))
    server_tags = TagM.get_by_ids(server.get('tag_ids', []))

    server_location = ServerLocationM.get_one(server.get('location_id')) if server.get('location_id') else None

    return render_template(
        'infra_module/servers/server_view.html',
        server=server,
        server_roles=server_roles,
        server_products=server_products,
        server_programs=server_programs,
        server_tags=server_tags,
        server_location=server_location,
    )


@servers_module.route('/new/', methods=['GET', 'POST'])
@access_required(UserRole.READWRITE)
def server_new():
    form = ServerForm()
    form.id.data = 'new'
    _populate_choices(form)

    if form.validate_on_submit():
        s_id = ServerM.create(
            name=form.name.data,
            role_ids=form.role_ids.data or [],
            ip_address=form.ip_address.data or '',
            url=form.url.data or '',
            os_=form.os.data or '',
            cpu=form.cpu.data or '',
            cpu_cores=form.cpu_cores.data or '',
            ram=form.ram.data or '',
            disk=form.disk.data or '',
            location_id=form.location_id.data,
            comments=form.comments.data or '',
            status=form.status.data,
            product_ids=form.product_ids.data or [],
            program_ids=form.program_ids.data or [],
            tag_ids=form.tag_ids.data or [],
        )
        flash(f'Server "{form.name.data}" created.', 'success')
        return redirect(url_for('servers_module.server_view', server_id=s_id))

    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field}: {error}', 'error')

    return render_template('infra_module/servers/server_form.html',
                           form=form, title='New Server', action='new')


@servers_module.route('/<int:server_id>/edit/', methods=['GET', 'POST'])
@access_required(UserRole.READWRITE)
def server_edit(server_id):
    server = ServerM.get_one(server_id)
    if not server:
        flash('Server not found.', 'error')
        return redirect(url_for('servers_module.servers_all'))

    form = ServerForm()
    form.id.data = str(server_id)
    _populate_choices(form)

    if request.method == 'GET':
        _prefill_form_from_server(form, server)

    elif form.validate_on_submit():
        ServerM.update(
            id_=server_id,
            name=form.name.data,
            role_ids=form.role_ids.data or [],
            ip_address=form.ip_address.data or '',
            url=form.url.data or '',
            os_=form.os.data or '',
            cpu=form.cpu.data or '',
            cpu_cores=form.cpu_cores.data or '',
            ram=form.ram.data or '',
            disk=form.disk.data or '',
            location_id=form.location_id.data,
            comments=form.comments.data or '',
            status=form.status.data,
            product_ids=form.product_ids.data or [],
            program_ids=form.program_ids.data or [],
            tag_ids=form.tag_ids.data or [],
        )
        flash(f'Server "{form.name.data}" updated.', 'success')
        return redirect(url_for('servers_module.server_view', server_id=server_id))

    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')

    return render_template('infra_module/servers/server_form.html',
                           form=form, title='Edit Server', action='edit',
                           server=server)


@servers_module.route('/<int:server_id>/copy/', methods=['GET', 'POST'])
@access_required(UserRole.READWRITE)
def server_copy(server_id):
    server = ServerM.get_one(server_id)
    if not server:
        flash('Server not found.', 'error')
        return redirect(url_for('servers_module.servers_all'))

    form = ServerForm()
    form.id.data = 'new'
    _populate_choices(form)

    if request.method == 'GET':
        _prefill_form_from_server(
            form, server,
            name=f"{server['name']} copy",
            include_ip_url=False,
        )
    elif form.validate_on_submit():
        s_id = ServerM.create(
            name=form.name.data,
            role_ids=form.role_ids.data or [],
            ip_address=form.ip_address.data or '',
            url=form.url.data or '',
            os_=form.os.data or '',
            cpu=form.cpu.data or '',
            cpu_cores=form.cpu_cores.data or '',
            ram=form.ram.data or '',
            disk=form.disk.data or '',
            location_id=form.location_id.data,
            comments=form.comments.data or '',
            status=form.status.data,
            product_ids=form.product_ids.data or [],
            program_ids=form.program_ids.data or [],
            tag_ids=form.tag_ids.data or [],
        )
        flash(f'Server "{form.name.data}" created.', 'success')
        return redirect(url_for('servers_module.server_view', server_id=s_id))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')

    return render_template('infra_module/servers/server_form.html',
                           form=form, title='Copy Server', action='new')


@servers_module.route('/<int:server_id>/delete/', methods=['POST'])
@access_required(UserRole.READWRITE)
def server_delete(server_id):
    server = ServerM.get_one(server_id)
    if not server:
        flash('Server not found.', 'error')
        return redirect(url_for('servers_module.servers_all'))

    ServerM.delete(server_id)
    flash(f'Server "{server["name"]}" deleted.', 'success')
    return redirect(url_for('servers_module.servers_all'))
