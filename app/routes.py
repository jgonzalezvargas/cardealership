from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app import app
from app.forms import LoginForm
from app.queries.users import query_user_login
from app.user import User
import sys

@app.route('/')
@app.route('/index')
@login_required
def index():
    print(current_user.name, file=sys.stderr)

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
        
        u = User(user_data['id'], user_data['name'], user_data['last_name'], user_data['email'], user_data['role'])
        
        login_user(u, remember=form.remember_me.data)
        
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
    
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
    
    

