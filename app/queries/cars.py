from autotools.db import Database, DatabaseInstances
from autotools.db.databases import TRANSACTIONS_DATABASE
from autotools.db.tables import Cardealership

def check_car_ppu(ppu):
    select_query = f"SELECT ppu from {Cardealership.CARS} WHERE ppu = %s LIMIT 1"
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    car_ppu = auto_db.execute_query(select_query, (ppu,)).fetchone()
    auto_db.close_connection()
    
    if car_ppu is None:
        return False
    return True

def check_car_chasis(chasis):
    select_query = f"SELECT chasis from {Cardealership.CARS} WHERE chasis = %s LIMIT 1"
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    car_chasis = auto_db.execute_query(select_query, (chasis,)).fetchone()
    auto_db.close_connection()
    
    if car_chasis is None:
        return False
    return True

def query_insert_car(ppu, chasis, brand, model, version, year):
    insert_query = f"INSERT INTO {Cardealership.CARS} (ppu, chasis, brand, model, version, year) VALUES (%s, %s, %s, %s, %s, %s) RETURNING car_id"
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    car_id = auto_db.execute_query(insert_query, info=(ppu, chasis, brand, model, version, year)).fetchone()
    auto_db.close_connection()
    
    return car_id[0]

def query_get_car_data(car_id):
    select_query = f"SELECT ppu, chasis, brand, model, version, year FROM {Cardealership.CARS} WHERE car_id = %s LIMIT 1"
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    car_data = auto_db.execute_query(select_query, (car_id, )).fetchone()
    auto_db.close_connection()
    data = {'ppu': car_data[0], 
            'chasis': car_data[1], 
            'brand': car_data[2], 
            'model': car_data[3],
            'version': car_data[4],
            'year': car_data[5]}
    return data

def get_car_ppu(car_id):
    select_query = f"SELECT ppu from {Cardealership.CARS} WHERE car_id = %s LIMIT 1"
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    car_ppu = auto_db.execute_query(select_query, (car_id,)).fetchone()
    auto_db.close_connection()
    return car_ppu[0]

def get_car_chasis(car_id):
    select_query = f"SELECT chasis from {Cardealership.CARS} WHERE car_id = %s LIMIT 1"
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    car_chasis = auto_db.execute_query(select_query, (car_id,)).fetchone()
    auto_db.close_connection()
    return car_chasis[0]

def update_car(car_id, ppu, chasis, brand, model, version, year):
    update_query = f"UPDATE {Cardealership.CARS} SET ppu = %s, chasis = %s, brand = %s, model = %s, version = %s, year = %s WHERE car_id = %s"
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    auto_db.execute_query(update_query, (ppu, chasis, brand, model, version, year, car_id))
    auto_db.close_connection()
    return True

def get_car_list():
    select_query = f"SELECT car_id, ppu, chasis, brand, model, version, year FROM {Cardealership.CARS} ORDER BY car_id DESC"
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    car_data = auto_db.read_as_pd(select_query)
    auto_db.close_connection()
    
    return car_data