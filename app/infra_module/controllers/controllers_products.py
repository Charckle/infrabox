from flask import (Blueprint, request, render_template, flash,
                   redirect, url_for)

from app.infra_module.forms import ProductForm
from app.infra_module.models import ProductM, ServerM
from app.infra_module.other import UserRole
from app.wrappers import access_required

products_module = Blueprint('products_module', __name__, url_prefix='/products')


@products_module.route('/', methods=['GET'])
@access_required()
def products_all():
    q = request.args.get('q', '').strip()
    products = ProductM.get_all({'q': q} if q else None)
    return render_template('infra_module/products/products_all.html',
                           products=products, q=q)


@products_module.route('/<int:product_id>/', methods=['GET'])
@access_required()
def product_view(product_id):
    product = ProductM.get_one(product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('products_module.products_all'))

    servers = [s for s in ServerM.get_all()
               if product_id in [int(p) for p in s.get('product_ids', [])]]

    return render_template('infra_module/products/product_view.html',
                           product=product, servers=servers)


@products_module.route('/new/', methods=['GET', 'POST'])
@access_required(UserRole.READWRITE)
def product_new():
    form = ProductForm()
    form.id.data = 'new'

    if form.validate_on_submit():
        p_id = ProductM.create(name=form.name.data, comments=form.comments.data or '')
        flash(f'Product "{form.name.data}" created.', 'success')
        return redirect(url_for('products_module.product_view', product_id=p_id))

    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field}: {error}', 'error')

    return render_template('infra_module/products/product_form.html',
                           form=form, title='New Product', action='new')


@products_module.route('/<int:product_id>/edit/', methods=['GET', 'POST'])
@access_required(UserRole.READWRITE)
def product_edit(product_id):
    product = ProductM.get_one(product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('products_module.products_all'))

    form = ProductForm()
    form.id.data = str(product_id)

    if request.method == 'GET':
        form.name.data = product['name']
        form.comments.data = product.get('comments', '')

    elif form.validate_on_submit():
        ProductM.update(product_id, name=form.name.data,
                        comments=form.comments.data or '')
        flash(f'Product "{form.name.data}" updated.', 'success')
        return redirect(url_for('products_module.product_view', product_id=product_id))

    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')

    return render_template('infra_module/products/product_form.html',
                           form=form, title='Edit Product', action='edit',
                           product=product)


@products_module.route('/<int:product_id>/delete/', methods=['POST'])
@access_required(UserRole.READWRITE)
def product_delete(product_id):
    product = ProductM.get_one(product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('products_module.products_all'))

    ProductM.delete(product_id)
    flash(f'Product "{product["name"]}" deleted.', 'success')
    return redirect(url_for('products_module.products_all'))
