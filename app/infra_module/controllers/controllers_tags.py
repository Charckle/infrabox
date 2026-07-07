from flask import (Blueprint, request, render_template, flash,
                   redirect, url_for)

from app.infra_module.forms import TagForm
from app.infra_module.models import TagM, ServerM
from app.infra_module.other import UserRole
from app.wrappers import access_required

tags_module = Blueprint('tags_module', __name__, url_prefix='/tags')


@tags_module.route('/', methods=['GET'])
@access_required()
def tags_all():
    q = request.args.get('q', '').strip()
    tags = TagM.get_all({'q': q} if q else None)
    return render_template('infra_module/tags/tags_all.html',
                           tags=tags, q=q)


@tags_module.route('/<int:tag_id>/', methods=['GET'])
@access_required()
def tag_view(tag_id):
    tag = TagM.get_one(tag_id)
    if not tag:
        flash('Tag not found.', 'error')
        return redirect(url_for('tags_module.tags_all'))

    servers = [s for s in ServerM.get_all()
               if tag_id in [int(t) for t in s.get('tag_ids', [])]]

    return render_template('infra_module/tags/tag_view.html',
                           tag=tag, servers=servers)


@tags_module.route('/new/', methods=['GET', 'POST'])
@access_required(UserRole.READWRITE)
def tag_new():
    form = TagForm()
    form.id.data = 'new'

    if form.validate_on_submit():
        t_id = TagM.create(
            name=form.name.data,
            color=form.color.data,
            comments=form.comments.data or '',
        )
        flash(f'Tag "{form.name.data}" created.', 'success')
        return redirect(url_for('tags_module.tag_view', tag_id=t_id))

    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field}: {error}', 'error')

    return render_template('infra_module/tags/tag_form.html',
                           form=form, title='New Tag', action='new')


@tags_module.route('/<int:tag_id>/edit/', methods=['GET', 'POST'])
@access_required(UserRole.READWRITE)
def tag_edit(tag_id):
    tag = TagM.get_one(tag_id)
    if not tag:
        flash('Tag not found.', 'error')
        return redirect(url_for('tags_module.tags_all'))

    form = TagForm()
    form.id.data = str(tag_id)

    if request.method == 'GET':
        form.name.data = tag['name']
        form.color.data = tag.get('color', '6c757d')
        form.comments.data = tag.get('comments', '')

    elif form.validate_on_submit():
        TagM.update(
            tag_id,
            name=form.name.data,
            color=form.color.data,
            comments=form.comments.data or '',
        )
        flash(f'Tag "{form.name.data}" updated.', 'success')
        return redirect(url_for('tags_module.tag_view', tag_id=tag_id))

    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')

    return render_template('infra_module/tags/tag_form.html',
                           form=form, title='Edit Tag', action='edit',
                           tag=tag)


@tags_module.route('/<int:tag_id>/delete/', methods=['POST'])
@access_required(UserRole.READWRITE)
def tag_delete(tag_id):
    tag = TagM.get_one(tag_id)
    if not tag:
        flash('Tag not found.', 'error')
        return redirect(url_for('tags_module.tags_all'))

    TagM.delete(tag_id)
    flash(f'Tag "{tag["name"]}" deleted.', 'success')
    return redirect(url_for('tags_module.tags_all'))
