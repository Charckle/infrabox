from flask import Flask, render_template, jsonify, send_from_directory, request, redirect, url_for, flash
from os import environ
import logging

from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect

load_dotenv()

from app import store

app = Flask(__name__)

env_config = environ.get('ENVCONFIG', 'DEV').upper()
if env_config == 'PROD':
    app.config.from_object('config.ProductionConfig')
else:
    app.config.from_object('config.DevelopmentConfig')

csrf = CSRFProtect(app)

# Configure and load JSON store
store.configure(app.config['DATA_DIR'])
store.load_all()

# Logging
logging_level_str = app.config.get('APP_LOGGING', 'INFO')
logging_level = getattr(logging, logging_level_str, logging.INFO)
app.logger.setLevel(logging_level)


def _path_matches(path: str, prefix: str) -> bool:
    """True if path equals prefix or is nested under it (trailing-slash insensitive)."""
    normalized = path.rstrip('/') or '/'
    prefix = prefix.rstrip('/') or '/'
    return normalized == prefix or normalized.startswith(prefix + '/')


def _read_only_write_allowed(path: str) -> bool:
    """Paths that may still mutate state while READ_ONLY_MODE is on."""
    return (
        _path_matches(path, '/login')
        or _path_matches(path, '/import-export/netbox')
        or _path_matches(path, '/import-export/infrabox/import')
    )


@app.before_request
def enforce_read_only_mode():
    if not app.config.get('READ_ONLY_MODE'):
        return None

    # Block all mutating requests except login + imports.
    # /setup/ POST is intentionally not allowlisted.
    if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
        if _read_only_write_allowed(request.path):
            return None
        flash('Instance is in read-only mode. Changes are not allowed.', 'error')
        if request.referrer:
            return redirect(request.referrer)
        return redirect(url_for('infra_module.index'))

    return None


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.route('/health')
def health():
    return jsonify(status='healthy'), 200


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico')


# Register blueprints
from app.infra_module.controllers.controllers import infra_module
from app.infra_module.controllers.controllers_servers import servers_module
from app.infra_module.controllers.controllers_roles import roles_module
from app.infra_module.controllers.controllers_products import products_module
from app.infra_module.controllers.controllers_programs import programs_module
from app.infra_module.controllers.controllers_tags import tags_module
from app.infra_module.controllers.controllers_locations import locations_module
from app.infra_module.controllers.controllers_import_export import import_export_module
from app.infra_module.controllers.controllers_admin import admin_module

app.register_blueprint(infra_module)
app.register_blueprint(servers_module)
app.register_blueprint(roles_module)
app.register_blueprint(products_module)
app.register_blueprint(programs_module)
app.register_blueprint(tags_module)
app.register_blueprint(locations_module)
app.register_blueprint(import_export_module)
app.register_blueprint(admin_module)


# Inject helpers into every template
from app.infra_module.models import ServerRoleM, ProductM, ProgramM, TagM, ServerLocationM, UserM, ServerM
from app.infra_module.other import UserRole, role_label, status_badge, color_badge_style, split_ip_addresses, SERVER_STATUS_CHOICES


BANNER = r"""
  _____        __           ____
 |_   _|      / _|         |  _ \
   | |  _ __ | |_ _ __ __ _| |_) | _____  __
   | | | '_ \|  _| '__/ _` |  _ < / _ \ \/ /
  _| |_| | | | | | | | (_| | |_) | (_) >  <
 |_____|_| |_|_| |_|  \__,_|____/ \___/_/\_\

-- Kevin, you did a good job, but THE FUTURE IS HERE, OLD MAN!
"""


@app.context_processor
def inject_globals():
    from flask import session
    current_user = None
    if session.get('user_id'):
        current_user = UserM.get_one(session['user_id'])
    read_only_mode = bool(app.config.get('READ_ONLY_MODE'))
    can_write = (
        not read_only_mode
        and current_user is not None
        and current_user.get('role', 99) <= UserRole.READWRITE.value
    )
    return dict(
        ServerRoleM=ServerRoleM,
        ProductM=ProductM,
        ProgramM=ProgramM,
        TagM=TagM,
        ServerLocationM=ServerLocationM,
        ServerM=ServerM,
        UserM=UserM,
        UserRole=UserRole,
        role_label=role_label,
        status_badge=status_badge,
        color_badge_style=color_badge_style,
        current_user=current_user,
        read_only_mode=read_only_mode,
        can_write=can_write,
        banner=BANNER,
        env_config=env_config,
    )


@app.template_filter('split_ips')
def split_ips_filter(value):
    return split_ip_addresses(value or '')


print(BANNER, flush=True)
print(f'Environment: {env_config}', flush=True)
if app.config.get('READ_ONLY_MODE'):
    print('Read-only mode: ON', flush=True)
app.logger.info(
    'InfraBox started (environment=%s, read_only=%s)',
    env_config,
    bool(app.config.get('READ_ONLY_MODE')),
)
