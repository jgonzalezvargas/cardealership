from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email
import sys

from app.queries.users import query_check_email

ROLES = ['-', 'Compras', 'Ventas', 'Manager', 'Admin']

class LoginForm(FlaskForm):
    username = StringField('User', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    
class RegistrationForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    last_name = StringField('Apellido', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    phone = StringField('Telefono', validators=[DataRequired()])
    role = SelectField('Rol', choices = ROLES, validators=[DataRequired()])
    submit = SubmitField('Crear Usuario')
    
    def validate_email(self, email):
        print('checking email', file=sys.stderr)
        if query_check_email(email=email.data):
            raise ValidationError("Ese Email ya esta registrado")
        
    def validate_role(self, role):
        print(role.data, file=sys.stderr)
        if role.data == '-':
            raise ValidationError("Seleccione un Rol")
        