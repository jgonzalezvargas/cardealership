from autotools.db import Database, DatabaseInstances
from autotools.db.databases import TRANSACTIONS_DATABASE
from autotools.db.tables import Cardealership

def query_insert_client(rut, client_name, client_last_name, email, adress, phone):
    insert_query = f"INSERT INTO {Cardealership.CLIENTS} (rut, client_name, client_last_name, address, email, phone) VALUES (%s, %s, %s, %s, %s, %s) RETURNING client_id"
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    client_id = auto_db.execute_query(insert_query, info=(rut, client_name, client_last_name, adress, email, phone)).fetchone()
    auto_db.close_connection()
    
    return client_id

def query_check_client_email(email):
    select_query = f"SELECT email from {Cardealership.CLIENTS} WHERE email = %s LIMIT 1"
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    user_email = auto_db.execute_query(select_query, (email,)).fetchone()
    auto_db.close_connection()
    
    if user_email is None:
        return False
    return True

def query_check_client_rut(rut):
    select_query = f"SELECT rut from {Cardealership.CLIENTS} WHERE rut = %s LIMIT 1"
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    user_email = auto_db.execute_query(select_query, (rut,)).fetchone()
    auto_db.close_connection()
    
    if user_email is None:
        return False
    return True

def query_get_client_data(client_id):
    select_query = f"SELECT client_name, client_last_name, email, rut, phone, address FROM {Cardealership.CLIENTS} WHERE client_id = %s LIMIT 1"
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    client_data = auto_db.execute_query(select_query, (client_id, )).fetchone()
    auto_db.close_connection()
    data = {'name': client_data[0], 
            'last_name': client_data[1], 
            'email': client_data[2], 
            'rut': client_data[3],
            'phone': client_data[4],
            'address': client_data[5]}
    return data

def get_client_rut(client_id):
    select_query = f"SELECT rut FROM {Cardealership.CLIENTS} WHERE client_id = %s LIMIT 1"
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    client_rut = auto_db.execute_query(select_query, (client_id, )).fetchone()
    auto_db.close_connection()
    return client_rut[0]

def get_client_email(client_id):
    select_query = f"SELECT email FROM {Cardealership.CLIENTS} WHERE client_id = %s LIMIT 1"
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    client_email = auto_db.execute_query(select_query, (client_id, )).fetchone()
    auto_db.close_connection()
    return client_email[0]

def update_client(client_id, client_name, client_last_name, phone, email, rut, address):
    update_query = f"UPDATE {Cardealership.CLIENTS} SET client_name = %s, client_last_name = %s, phone = %s, email = %s, rut = %s, address = %s WHERE client_id = %s"
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    auto_db.execute_query(update_query, (client_name, client_last_name, phone, email, rut, address, client_id))
    auto_db.close_connection()
    return True

def get_client_list():
    select_query = f"SELECT client_id, client_name, client_last_name, rut, email, phone FROM {Cardealership.CLIENTS} ORDER BY client_id DESC"
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    client_data = auto_db.read_as_pd(select_query)
    auto_db.close_connection()
    
    return client_data

def get_clientid_rut():
    select_query = f"SELECT client_id, rut FROM {Cardealership.CLIENTS} ORDER BY RUT DESC"
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    client_data = auto_db.read_as_pd(select_query)
    auto_db.close_connection()
    ordered_data = list()
    
    for _, client in client_data.iterrows():
        tup = (client.client_id, client.rut)
        ordered_data.append(tup)
    
    return ordered_data
    