from flask import (Blueprint, request, render_template, flash,
                   session, redirect, url_for)

from app.infra_module.forms import UserForm
from app.infra_module.models import UserM
from app.infra_module.other import UserRole, role_label
from app.wrappers import access_required

admin_module = Blueprint('admin_module', __name__, url_prefix='/admin')


@admin_module.route('/users/', methods=['GET'])
@access_required(UserRole.ADMIN)
def users_all():
    users = UserM.get_all()
    return render_template('infra_module/admin/users/users_all.html',
                           users=users, role_label=role_label)


@admin_module.route('/users/new/', methods=['GET', 'POST'])
@access_required(UserRole.ADMIN)
def user_new():
    form = UserForm()
    form.id.data = 'new'

    if form.validate_on_submit():
        if not form.password.data:
            flash('Password is required for a new user.', 'error')
            return render_template('infra_module/admin/users/user_form.html',
                                   form=form, title='New User', action='new')

        u_id = UserM.create(
            username=form.username.data,
            password=form.password.data,
            role=int(form.role.data),
            status=int(form.status.data),
        )
        flash(f'User "{form.username.data}" created.', 'success')
        return redirect(url_for('admin_module.user_edit', user_id=u_id))

    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field}: {error}', 'error')

    return render_template('infra_module/admin/users/user_form.html',
                           form=form, title='New User', action='new')


@admin_module.route('/users/<int:user_id>/edit/', methods=['GET', 'POST'])
@access_required(UserRole.ADMIN)
def user_edit(user_id):
    user = UserM.get_one(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin_module.users_all'))

    form = UserForm()
    form.id.data = str(user_id)

    if request.method == 'GET':
        form.username.data = user['username']
        form.role.data = str(user['role'])
        form.status.data = str(user['status'])

    elif form.validate_on_submit():
        # Guard: cannot disable last active admin
        if (user['status'] == 1 and int(form.status.data) == 0
                and len(UserM.get_all_active()) < 2):
            flash('Cannot disable the last active user.', 'error')
            return redirect(url_for('admin_module.user_edit', user_id=user_id))

        UserM.update(
            id_=user_id,
            username=form.username.data,
            role=int(form.role.data),
            status=int(form.status.data),
            password=form.password.data or None,
        )
        flash(f'User "{form.username.data}" updated.', 'success')
        return redirect(url_for('admin_module.user_edit', user_id=user_id))

    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')

    return render_template('infra_module/admin/users/user_form.html',
                           form=form, title='Edit User', action='edit', user=user)


@admin_module.route('/users/<int:user_id>/delete/', methods=['POST'])
@access_required(UserRole.ADMIN)
def user_delete(user_id):
    user = UserM.get_one(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin_module.users_all'))

    all_users = UserM.get_all()
    if len(all_users) < 2:
        flash('Cannot delete the last user.', 'error')
        return redirect(url_for('admin_module.users_all'))

    if user_id == session.get('user_id'):
        flash('Cannot delete yourself.', 'error')
        return redirect(url_for('admin_module.user_edit', user_id=user_id))

    confirm = request.form.get('confirm_username', '').strip()
    if confirm != user['username']:
        flash('Type the username exactly to confirm deletion.', 'error')
        return redirect(url_for('admin_module.user_edit', user_id=user_id))

    UserM.delete(user_id)
    flash(f'User "{user["username"]}" deleted.', 'success')
    return redirect(url_for('admin_module.users_all'))
