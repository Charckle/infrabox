from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (StringField, PasswordField, SelectField,
                     SelectMultipleField, TextAreaField, HiddenField,
                     SubmitField, validators)
from wtforms.validators import EqualTo, ValidationError

from app.infra_module.other import SERVER_STATUS_CHOICES, ROLE_CHOICES
from app.infra_module.models import UserM


class LoginForm(FlaskForm):
    username = StringField('Username', [validators.InputRequired(message='Username is required.')])
    password = PasswordField('Password', [validators.InputRequired(message='Password is required.')])
    submit = SubmitField('Sign In')


class SetupForm(FlaskForm):
    username = StringField('Username', [
        validators.InputRequired(),
        validators.Length(max=128),
    ])
    password = PasswordField('Password', [validators.InputRequired()])
    password_2 = PasswordField('Repeat Password', [
        validators.InputRequired(),
        EqualTo('password', message='Passwords must match.'),
    ])
    submit = SubmitField('Create admin account')


class UserForm(FlaskForm):
    id = HiddenField('id', [validators.InputRequired()])
    username = StringField('Username', [
        validators.InputRequired(),
        validators.Length(max=128),
    ])
    password = PasswordField('Password')
    password_2 = PasswordField('Repeat Password', [EqualTo('password', message='Passwords must match.')])
    role = SelectField('Role', [validators.InputRequired()], choices=ROLE_CHOICES, coerce=str)
    status = SelectField('Status', [validators.InputRequired()],
                         choices=[('1', 'Active'), ('0', 'Disabled')], coerce=str)
    submit = SubmitField('Save')

    def validate_username(self, username):
        existing = UserM.check_username(username.data, exclude_id=self.id.data)
        if existing:
            raise ValidationError('Username already taken.')


class ServerRoleForm(FlaskForm):
    id = HiddenField('id', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired(), validators.Length(max=100)])
    color = StringField('Color (hex)', [validators.InputRequired(), validators.Length(max=6)],
                        default='0d6efd')
    description = StringField('Description', [validators.Length(max=200)])
    submit = SubmitField('Save')


class ProductForm(FlaskForm):
    id = HiddenField('id', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired(), validators.Length(max=200)])
    comments = TextAreaField('Comments')
    submit = SubmitField('Save')


class ServerLocationForm(FlaskForm):
    id = HiddenField('id', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired(), validators.Length(max=200)])
    comments = TextAreaField('Comments')
    submit = SubmitField('Save')


class ProgramForm(FlaskForm):
    id = HiddenField('id', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired(), validators.Length(max=200)])
    comments = TextAreaField('Comments')
    submit = SubmitField('Save')


class TagForm(FlaskForm):
    id = HiddenField('id', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired(), validators.Length(max=100)])
    color = StringField('Color (hex)', [validators.InputRequired(), validators.Length(max=6)],
                        default='6c757d')
    comments = TextAreaField('Comments')
    submit = SubmitField('Save')


def _coerce_optional_int(value):
    if value is None or value == '':
        return None
    return int(value)


class ServerForm(FlaskForm):
    id = HiddenField('id', [validators.InputRequired()])
    name = StringField('Name', [validators.InputRequired(), validators.Length(max=200)])
    status = SelectField('Status', [validators.InputRequired()],
                         choices=SERVER_STATUS_CHOICES, coerce=str)
    ip_address = StringField('IP Address(es)', [validators.Length(max=255)])
    url = StringField('URL(s)', [validators.Length(max=255)])
    os = StringField('Operating System', [validators.Length(max=255)])
    cpu = StringField('CPU', [validators.Length(max=255)])
    cpu_cores = StringField('CPU Cores', [validators.Length(max=50)])
    ram = StringField('RAM', [validators.Length(max=100)])
    disk = StringField('Disk', [validators.Length(max=100)])
    location_id = SelectField('Server Location', [validators.Optional()], coerce=_coerce_optional_int)
    comments = TextAreaField('Comments')
    role_ids = SelectMultipleField('Server Roles', coerce=int)
    product_ids = SelectMultipleField('Products', coerce=int)
    program_ids = SelectMultipleField('Programs', coerce=int)
    tag_ids = SelectMultipleField('Tags', coerce=int)
    submit = SubmitField('Save')


class NetboxTagsImportForm(FlaskForm):
    import_file = FileField('Tags CSV file', validators=[
        FileRequired(message='Please choose a CSV file.'),
        FileAllowed(['csv'], 'CSV files only.'),
    ])
    submit = SubmitField('Import Tags')


class NetboxProgramsImportForm(FlaskForm):
    import_file = FileField('Programs CSV file', validators=[
        FileRequired(message='Please choose a CSV file.'),
        FileAllowed(['csv'], 'CSV files only.'),
    ])
    submit = SubmitField('Import Programs')


class NetboxProductsImportForm(FlaskForm):
    import_file = FileField('Products CSV file', validators=[
        FileRequired(message='Please choose a CSV file.'),
        FileAllowed(['csv'], 'CSV files only.'),
    ])
    submit = SubmitField('Import Products')


class NetboxServerRolesImportForm(FlaskForm):
    import_file = FileField('Server roles CSV file', validators=[
        FileRequired(message='Please choose a CSV file.'),
        FileAllowed(['csv'], 'CSV files only.'),
    ])
    submit = SubmitField('Import Server Roles')


class NetboxServersImportForm(FlaskForm):
    import_file = FileField('Servers CSV file', validators=[
        FileRequired(message='Please choose a CSV file.'),
        FileAllowed(['csv'], 'CSV files only.'),
    ])
    submit = SubmitField('Import Servers')


class InfraBoxFullBackupImportForm(FlaskForm):
    import_file = FileField('Full backup file', validators=[
        FileRequired(message='Please choose a backup file.'),
        FileAllowed(['ibxf'], 'InfraBox backup (.ibxf) only.'),
    ])
    submit = SubmitField('Import full backup')


class InfraBoxTagsImportForm(FlaskForm):
    import_file = FileField('Tags JSON file', validators=[
        FileRequired(message='Please choose a JSON file.'),
        FileAllowed(['json'], 'JSON files only.'),
    ])
    submit = SubmitField('Import Tags')


class InfraBoxServerRolesImportForm(FlaskForm):
    import_file = FileField('Server roles JSON file', validators=[
        FileRequired(message='Please choose a JSON file.'),
        FileAllowed(['json'], 'JSON files only.'),
    ])
    submit = SubmitField('Import Server Roles')


class InfraBoxProductsImportForm(FlaskForm):
    import_file = FileField('Products JSON file', validators=[
        FileRequired(message='Please choose a JSON file.'),
        FileAllowed(['json'], 'JSON files only.'),
    ])
    submit = SubmitField('Import Products')


class InfraBoxProgramsImportForm(FlaskForm):
    import_file = FileField('Programs JSON file', validators=[
        FileRequired(message='Please choose a JSON file.'),
        FileAllowed(['json'], 'JSON files only.'),
    ])
    submit = SubmitField('Import Programs')


class InfraBoxServerLocationsImportForm(FlaskForm):
    import_file = FileField('Server locations JSON file', validators=[
        FileRequired(message='Please choose a JSON file.'),
        FileAllowed(['json'], 'JSON files only.'),
    ])
    submit = SubmitField('Import Server Locations')


class InfraBoxServersImportForm(FlaskForm):
    import_file = FileField('Servers JSON file', validators=[
        FileRequired(message='Please choose a JSON file.'),
        FileAllowed(['json'], 'JSON files only.'),
    ])
    submit = SubmitField('Import Servers')


class InfraBoxUsersImportForm(FlaskForm):
    import_file = FileField('Users JSON file', validators=[
        FileRequired(message='Please choose a JSON file.'),
        FileAllowed(['json'], 'JSON files only.'),
    ])
    submit = SubmitField('Import Users')
