from flask import (Blueprint, request, render_template, flash,
                   redirect, url_for)

from app.infra_module.forms import ServerLocationForm
from app.infra_module.models import ServerLocationM, ServerM
from app.infra_module.other import UserRole
from app.wrappers import access_required

locations_module = Blueprint('locations_module', __name__, url_prefix='/locations')


@locations_module.route('/', methods=['GET'])
@access_required()
def locations_all():
    q = request.args.get('q', '').strip()
    locations = ServerLocationM.get_all({'q': q} if q else None)
    return render_template('infra_module/locations/locations_all.html',
                           locations=locations, q=q)


@locations_module.route('/<int:location_id>/', methods=['GET'])
@access_required()
def location_view(location_id):
    location = ServerLocationM.get_one(location_id)
    if not location:
        flash('Server location not found.', 'error')
        return redirect(url_for('locations_module.locations_all'))

    servers = [s for s in ServerM.get_all()
               if s.get('location_id') == location_id]

    return render_template('infra_module/locations/location_view.html',
                           location=location, servers=servers)


@locations_module.route('/new/', methods=['GET', 'POST'])
@access_required(UserRole.READWRITE)
def location_new():
    form = ServerLocationForm()
    form.id.data = 'new'

    if form.validate_on_submit():
        loc_id = ServerLocationM.create(name=form.name.data, comments=form.comments.data or '')
        flash(f'Server location "{form.name.data}" created.', 'success')
        return redirect(url_for('locations_module.location_view', location_id=loc_id))

    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field}: {error}', 'error')

    return render_template('infra_module/locations/location_form.html',
                           form=form, title='New Server Location', action='new')


@locations_module.route('/<int:location_id>/edit/', methods=['GET', 'POST'])
@access_required(UserRole.READWRITE)
def location_edit(location_id):
    location = ServerLocationM.get_one(location_id)
    if not location:
        flash('Server location not found.', 'error')
        return redirect(url_for('locations_module.locations_all'))

    form = ServerLocationForm()
    form.id.data = str(location_id)

    if request.method == 'GET':
        form.name.data = location['name']
        form.comments.data = location.get('comments', '')

    elif form.validate_on_submit():
        ServerLocationM.update(location_id, name=form.name.data,
                               comments=form.comments.data or '')
        flash(f'Server location "{form.name.data}" updated.', 'success')
        return redirect(url_for('locations_module.location_view', location_id=location_id))

    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')

    return render_template('infra_module/locations/location_form.html',
                           form=form, title='Edit Server Location', action='edit',
                           location=location)


@locations_module.route('/<int:location_id>/delete/', methods=['POST'])
@access_required(UserRole.READWRITE)
def location_delete(location_id):
    location = ServerLocationM.get_one(location_id)
    if not location:
        flash('Server location not found.', 'error')
        return redirect(url_for('locations_module.locations_all'))

    ServerLocationM.delete(location_id)
    flash(f'Server location "{location["name"]}" deleted.', 'success')
    return redirect(url_for('locations_module.locations_all'))
