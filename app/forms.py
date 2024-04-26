from typing import Mapping
from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email
from app.utilities import validate_rut, validate_rut_struct
import sys

from app.queries.users import query_check_email
from app.queries.clients import query_check_client_email, query_check_client_rut, get_client_email, get_client_rut
from app.queries.cars import check_car_chasis, check_car_ppu, get_car_ppu, get_car_chasis

ROLES = ['-', 'Compras', 'Ventas', 'Manager', 'Admin']
STATUS = [True, False]

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
        if query_check_email(email=email.data):
            raise ValidationError("Ese Email ya esta registrado")
        
    def validate_role(self, role):
        if role.data == '-':
            raise ValidationError("Seleccione un Rol")
        
class EditProfileForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    last_name = StringField('Apellido', validators=[DataRequired()])
    phone = StringField('Telefono', validators=[DataRequired()])
    submit = SubmitField('Editar Usuario')

class AdminEditUser(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    last_name = StringField('Apellido', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    phone = StringField('Telefono', validators=[DataRequired()])
    role = SelectField('Rol', choices = ROLES, validators=[DataRequired()])
    status = SelectField('Estado', choices = STATUS, validators=[DataRequired()])
    submit = SubmitField('Editar Usuario')
    
    def validate_role(self, role):
        if role.data == '-':
            raise ValidationError("Seleccione un Rol")
        

class CreateClient(FlaskForm):
    client_name = StringField('Nombre', validators=[DataRequired()])
    client_last_name = StringField('Apellido', validators=[DataRequired()])
    rut = StringField('RUT (debe ir sin puntos y con guion)', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    phone = StringField('Telefono', validators=[DataRequired()])
    address = StringField('Direccion', validators=[DataRequired()])
    submit = SubmitField('Crear Cliente')
    
    def validate_rut(self, rut):
        #STEP 1: Validar que el RUT sea real
        #STEP 1.1: Ver que lo ingresado tenga formato de RUT
        #TODO replace with RegEx
        if not validate_rut_struct(rut):
            raise ValidationError("Rut debe ir sin puntos y con guion")
        
        #STEP 1.2: Validar Numero con Dig. verificador
        if not validate_rut(rut.data):
            raise ValidationError("RUT invalido")
        
        #STEP 2: Verificar que no exista otro cliente con ese RUT
        if query_check_client_rut(rut=rut.data):
            raise ValidationError("Ya existe un cliente con ese RUT")
            
    
    def validate_email(self, email):
        if query_check_client_email(email=email.data):
            raise ValidationError("Ese Email ya esta registrado")
        
        
class EditClient(FlaskForm):
    client_name = StringField('Nombre', validators=[DataRequired()])
    client_last_name = StringField('Apellido', validators=[DataRequired()])
    rut = StringField('RUT (debe ir sin puntos y con guion)', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    phone = StringField('Telefono', validators=[DataRequired()])
    address = StringField('Direccion', validators=[DataRequired()])
    submit = SubmitField('Editar Cliente')  
    
    def __init__(self, client_id):
        super().__init__()
        self.client_id = client_id
  
    def validate_rut(self, rut):
        original_rut = get_client_rut(self.client_id)
        if rut.data != original_rut:
            #STEP 1: Validar que el RUT sea real
            #STEP 1.1: Ver que lo ingresado tenga formato de RUT
            #TODO replace with RegEx
            if not validate_rut_struct(rut):
                raise ValidationError("Rut debe ir sin puntos y con guion")
            
            #STEP 1.2: Validar Numero con Dig. verificador
            if not validate_rut(rut.data):
                raise ValidationError("RUT invalido")
            
            #STEP 2: Verificar que no exista otro cliente con ese RUT
            if query_check_client_rut(rut=rut.data):
                raise ValidationError("Ya existe un cliente con ese RUT")

    def validate_email(self, email):
        original_email = get_client_email(self.client_id)
        if email.data != original_email:
            if query_check_client_email(email=email.data):
                raise ValidationError("Ese Email ya esta registrado")
            
            
class CreateCar(FlaskForm):
    brand = StringField('Marca', validators=[DataRequired()])
    model = StringField('Modelo', validators=[DataRequired()])
    version = StringField('Versión', validators=[DataRequired()])
    year = StringField('Año', validators=[DataRequired()])
    ppu = StringField('PPU', validators=[DataRequired()])
    chasis = StringField('chasis', validators=[DataRequired()])
    submit = SubmitField('Crear Auto') 
    
    def validate_ppu(self, ppu):
        if check_car_ppu(ppu.data):
            raise ValidationError("Ya existe un auto con ese PPU")
        
    def validate_chasis(self, chasis):
        if check_car_chasis(chasis.data):
            raise ValidationError("Ya existe un auto con ese chasis")
        
        
class EditCar(FlaskForm):
    brand = StringField('Marca', validators=[DataRequired()])
    model = StringField('Modelo', validators=[DataRequired()])
    version = StringField('Versión', validators=[DataRequired()])
    year = StringField('Año', validators=[DataRequired()])
    ppu = StringField('PPU', validators=[DataRequired()])
    chasis = StringField('chasis', validators=[DataRequired()])
    submit = SubmitField('Editar Auto') 
    
    def __init__(self, car_id):
        super().__init__()
        self.car_id = car_id

    def validate_ppu(self, ppu):
        original_ppu = get_car_ppu(self.car_id)
        if ppu.data != original_ppu:
            if check_car_ppu(ppu.data):
                raise ValidationError("Ya existe un auto con ese PPU")

    def validate_chasis(self, chasis):
        original_chasis = get_car_chasis(self.car_id)
        if chasis.data != original_chasis:
            if check_car_ppu(chasis.data):
                raise ValidationError("Ya existe un auto con ese chasis")