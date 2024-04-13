from autotools.db import Database, DatabaseInstances
from autotools.db.databases import TRANSACTIONS_DATABASE
from autotools.db.tables import Cardealership
from app.utilities import hash_password

import sys

def query_get_user_data(user_id):
    select_query = f"SELECT name, last_name, email, role FROM {Cardealership.USERS} WHERE user_id = %s AND active_employee is TRUE LIMIT 1"
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    user_data = auto_db.execute_query(select_query, (user_id, )).fetchone()
    auto_db.close_connection()
    data = {'name': user_data[0], 
            'last_name': user_data[1], 
            'email': user_data[2], 
            'role': user_data[3]}
    return data
    
    
def query_user_login(email, passwd):
    hashed_passwd = hash_password(passwd)
    select_query = f"SELECT user_id, name, last_name, email, role FROM {Cardealership.USERS} WHERE email = %s and password = %s AND active_employee is TRUE LIMIT 1"
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    user_data = auto_db.execute_query(select_query, (email, hashed_passwd)).fetchone()
    auto_db.close_connection()
    
    if user_data is None:
        return None
    
    data = {'id': user_data[0],
            'name': user_data[1], 
            'last_name': user_data[2], 
            'email': user_data[3], 
            'role': user_data[4]}
    
    return data


def query_check_email(email):
    select_query = f"SELECT email from {Cardealership.USERS} WHERE email = %s LIMIT 1"
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    user_email = auto_db.execute_query(select_query, (email,)).fetchone()
    auto_db.close_connection()
    
    if user_email is None:
        return False
    return True

def query_insert_user(name, last_name, email, passwd, phone, role):
    hashed_psswd = hash_password(password=passwd)
    insert_query = f"INSERT INTO {Cardealership.USERS} (name, last_name, email, password, phone, role) VALUES (%s, %s, %s, %s, %s, %s)"
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    auto_db.execute_query(insert_query, info=(name, last_name, email, hashed_psswd, phone, role,))
    auto_db.close_connection()
    
    return True