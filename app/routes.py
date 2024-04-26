from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app
from app.forms import LoginForm, RegistrationForm, EditProfileForm, AdminEditUser, CreateClient, EditClient, CreateCar, EditCar
from app.queries.users import query_user_login, query_insert_user, query_get_user_data, update_user, get_user_list, get_complete_user_data, admin_update_user
from app.queries.clients import query_insert_client, query_get_client_data, update_client, get_client_list
from app.queries.cars import query_insert_car, query_get_car_data, update_car, get_car_list
from app.models.user import User
from app.models.client import Client
from app.models.car import Car
import sys

@app.route('/')
@app.route('/index')
@login_required
def index():
    
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        
        user_data = query_user_login(form.username.data, form.password.data)
        
        if user_data is None:
            flash('Invalid username or password')
            return redirect(url_for('login'))
        
        u = User(user_data['id'], user_data['name'], user_data['last_name'], user_data['email'], user_data['role'], user_data['phone'])
        
        login_user(u, remember=form.remember_me.data)
        
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
    
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
    
    
@app.route('/new_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if current_user.role != 'Admin':
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        
        #TODO GENERATE PASSWORD
        pswd = 'default'
        
        s = form.name.data, form.last_name.data, form.email.data, pswd, form.phone.data, form.role.data
        print(s, file=sys.stderr)
                
        insertion = query_insert_user(form.name.data, form.last_name.data, form.email.data, pswd, form.phone.data, form.role.data)
        
        #TODO SEND EMAIL WITH GENERATED PASSWORD TO USER
        
        if insertion:
            flash('Usuario creado exitosamente')
            return redirect(url_for('index'))
        flash('ERROR')
        return redirect(url_for('new_user'))
    return render_template('create_user.html', title='Crear usuario', form=form)


@app.route('/user/<userid>')
@login_required
def user(userid):
    if current_user.user_id != userid:
        return redirect(url_for('user', userid=current_user.user_id))
    user_data = query_get_user_data(userid)
    user = User(userid, user_data['name'], user_data['last_name'], user_data['email'], user_data['role'], user_data['phone'])
    return render_template('user.html', user=user)
    
    
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        
        current_user.name = form.name.data
        current_user.last_name = form.last_name.data
        current_user.phone = form.phone.data
        update_user(current_user.user_id, current_user.name, current_user.last_name, current_user.phone)
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.last_name.data = current_user.last_name
        form.phone.data = current_user.phone
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)
    
    
@app.route('/user_list', methods=['GET', 'POST'])
@login_required
def user_list():
    if current_user.role != 'Admin':
        return redirect(url_for('index'))
    
    users = list()
    user_data = get_user_list()
    for _, user in user_data.iterrows():
        loaded_user = User(user.user_id, user.username, user.last_name, user.email, user.role, user.phone, user.active_employee)
        users.append(loaded_user)
        
    return render_template('user_list.html', title='Lista de Usuarios', users=users)
    
    
@app.route('/admin_edit_user/<userid>', methods=['GET', 'POST'])
@login_required
def admin_edit_user(userid):
    if current_user.role != 'Admin':
        return redirect(url_for('index'))
    
    user_data = get_complete_user_data(userid)
    print(user_data, file=sys.stderr)
    u = User(userid, user_data['name'], user_data['last_name'], user_data['email'], user_data['role'], user_data['phone'], user_data['status'])
    
    form = AdminEditUser()
    if form.validate_on_submit():
        
        u.name = form.name.data
        u.last_name = form.last_name.data
        u.phone = form.phone.data
        u.email = form.email.data
        u.role = form.role.data
        u.status = form.status.data
        admin_update_user(user_id=u.user_id, name=u.name, last_name=u.last_name, phone=u.phone, email=u.email, role=u.role, status=u.status)
        flash('Your changes have been saved.')
        return redirect(url_for('user_list'))
    
    elif request.method == 'GET':
        print('status = ', u.status, file=sys.stderr)
        
        form.name.data = u.name
        form.last_name.data = u.last_name
        form.phone.data = u.phone
        form.email.data = u.email
        form.role.data = u.role
        form.status.data = u.status
        print('status = ', form.status.data, file=sys.stderr)
    
    return render_template('admin_edit_user.html', title='Edit Profile',
                           form=form, user=u)
    

@app.route('/new_client', methods=['GET', 'POST'])
@login_required
def new_client():
    form = CreateClient()
    if form.validate_on_submit():
        print(form.rut.data, form.client_name.data, form.client_last_name.data, form.email.data, form.address.data, form.phone.data, file=sys.stderr)
        client_id = query_insert_client(form.rut.data, form.client_name.data, form.client_last_name.data, form.email.data, form.address.data, form.phone.data)
        print(client_id, file=sys.stderr)
        if client_id:
            flash('Cliente creado exitosamente')
            #TODO redirect to client page
            return redirect(url_for('client_profile', client_id=client_id[0]))
        flash('ERROR')
        return redirect(url_for('new_client'))
    return render_template('create_client.html', title='Crear Cliente', form=form)


@app.route('/client/<client_id>')
@login_required
def client_profile(client_id):
    client_data = query_get_client_data(client_id)
    client = Client(client_id = client_id, client_name=client_data['name'], client_last_name=client_data['last_name'], email=client_data['email'], rut=client_data['rut'], phone=client_data['phone'], address=client_data['address'])
    return render_template('client_profile.html', title=client.client_name + ' ' + client.client_last_name, client=client)


@app.route('/edit_client/<client_id>', methods=['GET', 'POST'])
@login_required
def edit_client(client_id):

    client_data = query_get_client_data(client_id)

    client = Client(client_id = client_id, client_name=client_data['name'], client_last_name=client_data['last_name'], email=client_data['email'], rut=client_data['rut'], phone=client_data['phone'], address=client_data['address'])
    
    form = EditClient(client_id)
    if form.validate_on_submit():
        client.client_name = form.client_name.data
        client.client_last_name = form.client_last_name.data
        client.phone = form.phone.data
        client.email = form.email.data
        client.rut = form.rut.data
        client.address = form.address.data
        
        update_client(client_id=client_id, client_name=client.client_name, client_last_name=client.client_last_name, phone=client.phone, email=client.email, rut=client.rut, address=client.address)
        flash('Your changes have been saved.')
        return redirect(url_for('client_profile', client_id=client_id))
    
    elif request.method == 'GET':       
        form.client_name.data = client.client_name
        form.client_last_name.data = client.client_last_name
        form.phone.data = client.phone
        form.email.data = client.email
        form.rut.data = client.rut
        form.address.data = client.address
    
    return render_template('edit_client.html', title='Edit Profile',
                           form=form, client=client)
    
    
@app.route('/client_list', methods=['GET', 'POST'])
@login_required
def client_list():
    clients = list()
    client_data = get_client_list()
    for _, client in client_data.iterrows():
        loaded_client = Client(client.client_id, client.rut, client.client_name, client.client_last_name, email=client.email, phone=client.phone)
        clients.append(loaded_client)
        
    return render_template('client_list.html', title='Lista de Clientes', clients=clients)    


@app.route('/new_car', methods=['GET', 'POST'])
@login_required
def create_car():
    form = CreateCar()
    if form.validate_on_submit():
        car_id = query_insert_car(form.ppu.data, form.chasis.data, form.brand.data, form.model.data, form.version.data, form.year.data)

        if car_id:
            flash('Auto creado exitosamente')
            return redirect(url_for('car_profile', car_id=car_id))
        flash('ERROR')
        return redirect(url_for('create_car'))
    return render_template('create_car.html', title='Crear Auto', form=form)


@app.route('/car/<car_id>')
@login_required
def car_profile(car_id):
    car_data = query_get_car_data(car_id)
    car = Car(car_id, car_data['ppu'], car_data['chasis'], car_data['brand'], car_data['model'], car_data['version'], car_data['year'])
    return render_template('car_profile.html', title=car.brand + ' ' + car.model + ' ' + car.ppu, car=car)


@app.route('/edit_car/<car_id>', methods=['GET', 'POST'])
@login_required
def edit_car(car_id):

    car_data = query_get_car_data(car_id)

    car = Car(car_id, car_data['ppu'], car_data['chasis'], car_data['brand'], car_data['model'], car_data['version'], car_data['year'])
    
    form = EditCar(car_id)
    if form.validate_on_submit():
        car.ppu = form.ppu.data
        car.chasis = form.chasis.data
        car.brand = form.brand.data
        car.model = form.model.data
        car.version = form.version.data
        car.year = form.year.data
        
        update_car(car_id, car.ppu, car.chasis, car.brand, car.model, car.version, car.year)
        flash('Your changes have been saved.')
        return redirect(url_for('car_profile', car_id=car_id))
    
    elif request.method == 'GET':       
        form.ppu.data = car.ppu
        form.chasis.data = car.chasis
        form.brand.data = car.brand
        form.model.data = car.model
        form.version.data = car.version
        form.year.data = car.year
    
    return render_template('edit_car.html', title='Edit Car', form=form)


@app.route('/car_list', methods=['GET', 'POST'])
@login_required
def car_list():
    cars = list()
    car_data = get_car_list()
    for _, car in car_data.iterrows():
        loaded_client = Car(car.car_id, car.ppu, car.chasis, car.brand, car.model, car.version, car.year)
        cars.append(loaded_client)
        
    return render_template('car_list.html', title='Lista de Autos', cars=cars)    