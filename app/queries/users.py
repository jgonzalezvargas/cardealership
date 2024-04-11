from autotools.db import Database, DatabaseInstances
from autotools.db.databases import TRANSACTIONS_DATABASE
from app.utilities import hash_password

import sys

def query_get_user_data(user_id):
    select_query = "SELECT name, last_name, email, role FROM users WHERE user_id = %s AND active_employee is TRUE LIMIT 1"
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
    select_query = "SELECT user_id, name, last_name, email, role FROM users WHERE email = %s and password = %s AND active_employee is TRUE LIMIT 1"
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    user_data = auto_db.execute_query(select_query, (email, hashed_passwd)).fetchone()
    auto_db.close_connection()
    
    print(user_data, file=sys.stderr)
    
    if user_data is None:
        return None
    
    data = {'id': user_data[0],
            'name': user_data[1], 
            'last_name': user_data[2], 
            'email': user_data[3], 
            'role': user_data[4]}
    
    return data