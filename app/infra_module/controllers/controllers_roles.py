from flask import (Blueprint, request, render_template, flash,
                   redirect, url_for)

from app.infra_module.forms import ServerRoleForm
from app.infra_module.models import ServerRoleM, ServerM
from app.infra_module.other import UserRole
from app.wrappers import access_required

roles_module = Blueprint('roles_module', __name__, url_prefix='/roles')


@roles_module.route('/', methods=['GET'])
@access_required()
def roles_all():
    q = request.args.get('q', '').lower().strip()
    roles = ServerRoleM.get_all()
    if q:
        roles = [r for r in roles if q in r.get('name', '').lower()]
    return render_template('infra_module/server_roles/roles_all.html',
                           roles=roles, q=q)


@roles_module.route('/<int:role_id>/', methods=['GET'])
@access_required()
def role_view(role_id):
    role = ServerRoleM.get_one(role_id)
    if not role:
        flash('Role not found.', 'error')
        return redirect(url_for('roles_module.roles_all'))

    servers = [s for s in ServerM.get_all()
               if role_id in [int(r) for r in s.get('role_ids', [])]]

    return render_template('infra_module/server_roles/role_view.html',
                           role=role, servers=servers)


@roles_module.route('/new/', methods=['GET', 'POST'])
@access_required(UserRole.READWRITE)
def role_new():
    form = ServerRoleForm()
    form.id.data = 'new'

    if form.validate_on_submit():
        r_id = ServerRoleM.create(
            name=form.name.data,
            color=form.color.data,
            description=form.description.data or '',
        )
        flash(f'Role "{form.name.data}" created.', 'success')
        return redirect(url_for('roles_module.role_view', role_id=r_id))

    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field}: {error}', 'error')

    return render_template('infra_module/server_roles/role_form.html',
                           form=form, title='New Role', action='new')


@roles_module.route('/<int:role_id>/edit/', methods=['GET', 'POST'])
@access_required(UserRole.READWRITE)
def role_edit(role_id):
    role = ServerRoleM.get_one(role_id)
    if not role:
        flash('Role not found.', 'error')
        return redirect(url_for('roles_module.roles_all'))

    form = ServerRoleForm()
    form.id.data = str(role_id)

    if request.method == 'GET':
        form.name.data = role['name']
        form.color.data = role.get('color', '0d6efd')
        form.description.data = role.get('description', '')

    elif form.validate_on_submit():
        ServerRoleM.update(
            id_=role_id,
            name=form.name.data,
            color=form.color.data,
            description=form.description.data or '',
        )
        flash(f'Role "{form.name.data}" updated.', 'success')
        return redirect(url_for('roles_module.role_view', role_id=role_id))

    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')

    return render_template('infra_module/server_roles/role_form.html',
                           form=form, title='Edit Role', action='edit', role=role)


@roles_module.route('/<int:role_id>/delete/', methods=['POST'])
@access_required(UserRole.READWRITE)
def role_delete(role_id):
    role = ServerRoleM.get_one(role_id)
    if not role:
        flash('Role not found.', 'error')
        return redirect(url_for('roles_module.roles_all'))

    ServerRoleM.delete(role_id)
    flash(f'Role "{role["name"]}" deleted.', 'success')
    return redirect(url_for('roles_module.roles_all'))
