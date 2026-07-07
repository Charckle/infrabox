from flask import (Blueprint, request, render_template, flash,
                   redirect, url_for)

from app.infra_module.forms import ProgramForm
from app.infra_module.models import ProgramM, ServerM
from app.infra_module.other import UserRole
from app.wrappers import access_required

programs_module = Blueprint('programs_module', __name__, url_prefix='/programs')


@programs_module.route('/', methods=['GET'])
@access_required()
def programs_all():
    q = request.args.get('q', '').strip()
    programs = ProgramM.get_all({'q': q} if q else None)
    return render_template('infra_module/programs/programs_all.html',
                           programs=programs, q=q)


@programs_module.route('/<int:program_id>/', methods=['GET'])
@access_required()
def program_view(program_id):
    program = ProgramM.get_one(program_id)
    if not program:
        flash('Program not found.', 'error')
        return redirect(url_for('programs_module.programs_all'))

    servers = [s for s in ServerM.get_all()
               if program_id in [int(p) for p in s.get('program_ids', [])]]

    return render_template('infra_module/programs/program_view.html',
                           program=program, servers=servers)


@programs_module.route('/new/', methods=['GET', 'POST'])
@access_required(UserRole.READWRITE)
def program_new():
    form = ProgramForm()
    form.id.data = 'new'

    if form.validate_on_submit():
        p_id = ProgramM.create(name=form.name.data, comments=form.comments.data or '')
        flash(f'Program "{form.name.data}" created.', 'success')
        return redirect(url_for('programs_module.program_view', program_id=p_id))

    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field}: {error}', 'error')

    return render_template('infra_module/programs/program_form.html',
                           form=form, title='New Program', action='new')


@programs_module.route('/<int:program_id>/edit/', methods=['GET', 'POST'])
@access_required(UserRole.READWRITE)
def program_edit(program_id):
    program = ProgramM.get_one(program_id)
    if not program:
        flash('Program not found.', 'error')
        return redirect(url_for('programs_module.programs_all'))

    form = ProgramForm()
    form.id.data = str(program_id)

    if request.method == 'GET':
        form.name.data = program['name']
        form.comments.data = program.get('comments', '')

    elif form.validate_on_submit():
        ProgramM.update(program_id, name=form.name.data,
                        comments=form.comments.data or '')
        flash(f'Program "{form.name.data}" updated.', 'success')
        return redirect(url_for('programs_module.program_view', program_id=program_id))

    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')

    return render_template('infra_module/programs/program_form.html',
                           form=form, title='Edit Program', action='edit',
                           program=program)


@programs_module.route('/<int:program_id>/delete/', methods=['POST'])
@access_required(UserRole.READWRITE)
def program_delete(program_id):
    program = ProgramM.get_one(program_id)
    if not program:
        flash('Program not found.', 'error')
        return redirect(url_for('programs_module.programs_all'))

    ProgramM.delete(program_id)
    flash(f'Program "{program["name"]}" deleted.', 'success')
    return redirect(url_for('programs_module.programs_all'))
