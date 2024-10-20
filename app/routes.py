from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app
from app.forms import LoginForm, RegistrationForm, EditProfileForm, AdminEditUser, CreateClient, EditClient, CreateCar, EditCar, CreatePurchase, CreateSale
from app.queries.users import query_user_login, query_insert_user, query_get_user_data, update_user, get_user_list, get_complete_user_data, admin_update_user
from app.queries.clients import query_insert_client, query_get_client_data, update_client, get_client_list
from app.queries.cars import query_insert_car, query_get_car_data, update_car, get_car_list
from app.queries.purchases import query_insert_purchases, get_purchases_list, get_purchase
from app.queries.sales import query_insert_sale, get_sales_list, get_sale
from app.queries.prices import get_prices
from app.models.user import User
from app.models.client import Client
from app.models.car import Car
from app.models.purchase import Purchase
from app.models.prices import Price
from app.models.sale import Sale
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
    if current_user.user_id != userid or current_user.role != 'Admin':
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


@app.route('/new_purchase/', methods=['GET', 'POST'])
@login_required
def new_purchase():
    form = CreatePurchase()
    if form.validate_on_submit():
        forms_data = [form.client_id.data, 
             form.car_id.data, 
             form.mileage.data, 
             form.car_color.data, 
             form.purchase_date.data, 
             form.car_price.data, 
             form.negotiated_price.data, 
             form.management.data, 
             form.bill_number.data
             ]
        print(forms_data, file=sys.stderr)
        
        p_id = query_insert_purchases(current_user.user_id,
                                        form.car_id.data,
                                        form.client_id.data,
                                        form.mileage.data, 
                                        form.car_color.data, 
                                        form.purchase_date.data, 
                                        form.car_price.data, 
                                        form.negotiated_price.data, 
                                        form.management.data, 
                                        form.bill_number.data)

        if p_id:
            flash('Compra ingresada exitosamente')
            return redirect(url_for('purchase', purchase_id=p_id))
        flash('ERROR')
        return redirect(url_for('new_purchase'))
    return render_template('create_purchase.html', title='Ingresar Compra', form=form)

#TODO add initial client_id / car_id

@app.route('/purchases_list', methods=['GET', 'POST'])
@login_required
def purchases_list():
    purchases = list()
    purchase_data = get_purchases_list()
    for _, p in purchase_data.iterrows():
        user = User(user_id = p.user_id, name=p.username, last_name=p.last_name)
        client = Client(client_id=p.client_id, client_name=p.client_name, client_last_name=p.client_last_name)
        car = Car(car_id=p.car_id, brand=p.brand, model=p.model, version=p.version, ppu=p.ppu)
        loaded_purchase = Purchase(p.purchase_id, user, client, car, p.mileage, p.purchase_date, p.price, p.negotiated_price, p.management, p.stock)
        purchases.append(loaded_purchase)
        
    return render_template('purchases_list.html', title='Lista de Consignaciones', purchases=purchases)    


@app.route('/purchase/<purchase_id>', methods=['GET', 'POST'])
@login_required
def purchase(purchase_id):
    client_data, car_data, purchase_data = get_purchase(purchase_id)
    prices = get_prices(purchase_id)
    price_list = list()
    for _, row in prices.iterrows():
        price = Price(row.price, row.datetime)
        price_list.append(price)
    client = Client(client_id=client_data['client_id'], client_name=client_data['client_name'], client_last_name=client_data['client_last_name'], rut=client_data['rut'], phone=client_data['phone'])
    car = Car(car_id=car_data['car_id'], brand=car_data['brand'], model=car_data['model'], version=car_data['version'], ppu=car_data['ppu'], year=car_data['year'], chasis=car_data['chasis'])
    purchase = Purchase(purchase_id=purchase_id, client=client, car=car, 
                        mileage=purchase_data['mileage'], purchase_date=purchase_data['purchase_date'], negotiated_price=purchase_data['negotiated_price'], car_color= purchase_data['car_color'],
                        bill_number=purchase_data['bill_number'], management=purchase_data['management'], stock=purchase_data['stock'], prices=price_list)
        
    return render_template('purchase.html', title=f'Consignación de {car.ppu}', purchase=purchase)    








@app.route('/new_sale/', methods=['GET', 'POST'])
@login_required
def new_sale():
    form = CreateSale()
    if form.validate_on_submit():
        forms_data = [form.client_id.data,
                      form.car_id.data,
                      form.sale_date.data,
                      form.sale_price.data,
                      form.real_cost.data,
                      form.source.data,
                      form.credit_comission.data,
                      form.card.data,
                      form.credit.data,
                      form.car_as_payment.data,
                      form.mileage.data,
                      form.car_color.data
             ]
        print(forms_data, file=sys.stderr)

        s_id = query_insert_sale(current_user.user_id,
                                        form.client_id.data,
                                        form.car_id.data,
                                        form.sale_date.data,
                                        form.sale_price.data,
                                        form.real_cost.data,
                                        form.source.data,
                                        form.credit_comission.data,
                                        form.card.data,
                                        form.credit.data,
                                        form.car_as_payment.data,
                                        form.mileage.data,
                                        form.car_color.data)

        if s_id:
            flash('Venta ingresada exitosamente')
            return redirect(url_for('sale', sale_id=s_id))
        flash('ERROR')
        return redirect(url_for('new_sale'))
    return render_template('create_sale.html', title='Ingresar Venta', form=form)




@app.route('/sales_list', methods=['GET', 'POST'])
@login_required
def sales_list():
    sales = list()
    sales_data = get_sales_list()
    for _, s in sales_data.iterrows():
        user = User(user_id = s.user_id, name=s.username, last_name=s.last_name)
        client = Client(client_id=s.client_id, client_name=s.client_name, client_last_name=s.client_last_name)
        car = Car(car_id=s.car_id, brand=s.brand, model=s.model, version=s.version, ppu=s.ppu)
        loaded_sale = Sale(s.sale_id, car=car, client=client, user=user, sale_date=s.sale_date, mileage=s.mileage, 
                           car_color=s.car_color, sale_price=s.sale_price, real_cost=s.real_cost, real_margin=s.real_margin,
                           source=s.source, stock=s.stock)
        sales.append(loaded_sale)
        
    return render_template('sales_list.html', title='Lista de Consignaciones', sales=sales)    


@app.route('/sale/<sale_id>', methods=['GET', 'POST'])
@login_required
def sale(sale_id):
    client_data, car_data, sale_data = get_sale(sale_id)

    client = Client(client_id=client_data['client_id'], client_name=client_data['client_name'], client_last_name=client_data['client_last_name'], rut=client_data['rut'], phone=client_data['phone'])
    car = Car(car_id=car_data['car_id'], brand=car_data['brand'], model=car_data['model'], version=car_data['version'], ppu=car_data['ppu'], year=car_data['year'], chasis=car_data['chasis'])
    sale = Sale(sale_id=sale_id, client=client, car=car, 
                        mileage=sale_data['mileage'], sale_date=sale_data['sale_date'], dhv=sale_data['dhv'], week=sale_data['week'], car_color=sale_data['car_color'],
                        sale_price=sale_data['sale_price'], real_cost=sale_data['real_cost'], real_margin=sale_data['real_margin'], source=sale_data['source'],
                        stock=sale_data['stock_val'], credit_comission=sale_data['credit_comission'], credit=sale_data['credit'], card=sale_data['card'],
                        car_as_payment=sale_data['car_as_payment'])
    
    
    
        
    return render_template('sale.html', title=f'Venta de {car.ppu}', sale=sale) 