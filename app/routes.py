from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app
from app.forms import LoginForm, RegistrationForm, EditProfileForm, AdminEditUser
from app.queries.users import query_user_login, query_insert_user, query_get_user_data, update_user, get_user_list, get_complete_user_data, admin_update_user
from app.user import User
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