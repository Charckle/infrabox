import base64

from flask import (Blueprint, request, render_template, flash,
                   session, redirect, url_for)

from app.infra_module.forms import LoginForm, SetupForm
from app.infra_module.models import UserM, ServerM, ServerRoleM, ProductM, ProgramM, TagM
from app.infra_module.other import UserRole
from app.wrappers import access_required

infra_module = Blueprint('infra_module', __name__, url_prefix='/')


@infra_module.route('/', methods=['GET'])
@access_required()
def index():
    server_count = len(ServerM.get_all())
    role_count = len(ServerRoleM.get_all())
    product_count = len(ProductM.get_all())
    program_count = len(ProgramM.get_all())
    tag_count = len(TagM.get_all())
    recent_servers = ServerM.get_all()[-5:][::-1]

    return render_template(
        'infra_module/index.html',
        server_count=server_count,
        role_count=role_count,
        product_count=product_count,
        program_count=program_count,
        tag_count=tag_count,
        recent_servers=recent_servers,
    )


@infra_module.route('/setup/', methods=['GET', 'POST'])
def setup():
    if not UserM.needs_setup():
        return redirect(url_for('infra_module.login'))

    form = SetupForm()

    if form.validate_on_submit():
        if not UserM.needs_setup():
            return redirect(url_for('infra_module.login'))

        user_id = UserM.create(
            username=form.username.data,
            password=form.password.data,
            role=UserRole.ADMIN.value,
            status=1,
        )
        form.password.data = None
        form.password_2.data = None

        session['user_id'] = user_id
        session['user_role'] = UserRole.ADMIN.value
        session.permanent = True
        flash(f'Admin account "{form.username.data}" created.', 'success')
        return redirect(url_for('infra_module.index'))

    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field}: {error}', 'error')

    return render_template('infra_module/auth/setup.html', form=form)


@infra_module.route('/login/', methods=['GET', 'POST'])
@infra_module.route('/login/<w_url>', methods=['GET', 'POST'])
def login(w_url=None):
    if UserM.needs_setup():
        return redirect(url_for('infra_module.setup'))

    if 'user_id' in session:
        return redirect(url_for('infra_module.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = UserM.login_check(form.username.data, form.password.data)
        form.password.data = None

        if user:
            session['user_id'] = user['id']
            session['user_role'] = user['role']
            session.permanent = True

            if w_url:
                try:
                    dest = base64.urlsafe_b64decode(w_url.encode()).decode()
                    return redirect(dest)
                except Exception:
                    pass

            return redirect(url_for('infra_module.index'))

        flash('Invalid username or password.', 'error')

    return render_template('infra_module/auth/login.html', form=form)


@infra_module.route('/logout/')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('infra_module.login'))
