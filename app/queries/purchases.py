from autotools.db import Database, DatabaseInstances
from autotools.db.databases import TRANSACTIONS_DATABASE
from autotools.db.tables import Cardealership
import sys

def query_insert_purchases(user_id, car_id, client_id, mileage, car_color, purchase_date, car_price, negotiated_price, management, bill_number):
    insert_purchase_query = f"""INSERT INTO {Cardealership.PURCHASES} (user_id, car_id, client_id, mileage, car_color, purchase_date, negotiated_price, management_id, bill_number) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING purchase_id"""
                        
    #print(insert_price_query%(purchase_id, user_id, car_price), file=sys.stderr)
                        
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    p_id = auto_db.execute_query(insert_purchase_query, info=(user_id, car_id, client_id, mileage, car_color, purchase_date, negotiated_price, management, bill_number)).fetchone()
    purchase_id = p_id[0]
    
    insert_price_query = f"""INSERT INTO {Cardealership.PRICES} (purchase_id, user_id, price, datetime) VALUES (%s, %s, %s, current_timestamp)"""
    auto_db.execute_query(insert_price_query, info=(purchase_id, user_id, car_price))
    
    #SELECT purchase_sale_id
    #TODO This can be improved so much
    #CONSTRAINT: The same car can't have more than one entry in purchase_sale_id without completion
    select_purchase_sale_id_query = f"""SELECT purchase_sale_id, sale_id FROM {Cardealership.PURCHASE_SALE} WHERE car_id = %s AND sale_id IS NOT NULL AND purchase_id IS NULL LIMIT 1"""
    ps_id = auto_db.execute_query(select_purchase_sale_id_query, info=(car_id,)).fetchone()
    if ps_id:
        purchase_sale_id = ps_id[0]
        sale_id = ps_id[1]
        update_query = f"""UPDATE {Cardealership.PURCHASE_SALE} SET purchase_id = %s WHERE purchase_sale_id = %s AND sale_id = %s AND car_id = %s"""
        auto_db.execute_query(update_query, info=(purchase_id, purchase_sale_id, sale_id, car_id))
    else:
        insert_purchase_sale_query = f"""INSERT INTO {Cardealership.PURCHASE_SALE} (purchase_id, sale_id, car_id, stock_id) VALUES (%s, %s, %s, %s)"""
        auto_db.execute_query(insert_purchase_sale_query, info=(purchase_id, None, car_id, 3)) #stock_id 3 => 'Stock' (en venta)
    
    
    auto_db.close_connection()
    
    return purchase_id


def get_purchases_list():
    query = f"""SELECT p.purchase_id, cl.client_id, c.car_id, u.user_id, 
                client_name, client_last_name, 
                brand, model, version, ppu, 
                mileage, purchase_date, negotiated_price, 
                price, max(pr.datetime), m.value as management, stock_val as stock, 
                u.name as username, u.last_name 
                FROM {Cardealership.PURCHASES} as p 
                JOIN {Cardealership.CARS} as c ON (c.car_id = p.car_id) 
                JOIN {Cardealership.CLIENTS} as cl on (p.client_id = cl.client_id) 
                JOIN {Cardealership.USERS} as u on (p.user_id =  u.user_id) 
                JOIN {Cardealership.MANAGEMENT} as m ON (p.management_id = m.management_id) 
                JOIN {Cardealership.PURCHASE_SALE} as ps ON (p.purchase_id = ps.purchase_id) 
                JOIN {Cardealership.STOCK_STATUS} as ss ON (ps.stock_id = ss.stock_id) 
                JOIN {Cardealership.PRICES} as pr ON (pr.purchase_id = p.purchase_id) 
                GROUP BY client_name, client_last_name, pr.datetime, brand, model, version, ppu, mileage, purchase_date, negotiated_price, price, m.value, ss.stock_val, u.name, u.last_name, cl.client_id, 
                c.car_id, u.user_id, p.purchase_id 
                ORDER BY purchase_date DESC"""
                
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    purchases_data = auto_db.read_as_pd(query)
    auto_db.close_connection()
    
    return purchases_data


def get_purchase(purchase_id):
    query = f"""SELECT cl.client_id, c.car_id,
                client_name, client_last_name, rut, cl.phone,
                brand, model, version, ppu, year, chasis,
                mileage, purchase_date, negotiated_price, bill_number,
                m.value as management, stock_val as stock, car_color
                FROM {Cardealership.PURCHASES} as p 
                JOIN {Cardealership.CARS} as c ON (c.car_id = p.car_id) 
                JOIN {Cardealership.CLIENTS} as cl on (p.client_id = cl.client_id) 
                JOIN {Cardealership.MANAGEMENT} as m ON (p.management_id = m.management_id) 
                JOIN {Cardealership.PURCHASE_SALE} as ps ON (p.purchase_id = ps.purchase_id) 
                JOIN {Cardealership.STOCK_STATUS} as ss ON (ps.stock_id = ss.stock_id) 
                JOIN {Cardealership.PRICES} as pr ON (pr.purchase_id = p.purchase_id) 
                WHERE p.purchase_id = %s LIMIT 1"""
    #TODO Maybe reorder the JOINS
    print(query%(purchase_id,), sys.stderr)
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    purchases_data = auto_db.execute_query(query, info=(purchase_id,)).fetchone()
    auto_db.close_connection()
    
    client_data = {'client_id': purchases_data[0],
                   'client_name': purchases_data[2],
                   'client_last_name': purchases_data[3],
                   'rut': purchases_data[4],
                   'phone': purchases_data[5],
                   }
    
    car_data = {'car_id': purchases_data[1],
                'brand': purchases_data[6],
                'model': purchases_data[7],
                'version': purchases_data[8],
                'ppu': purchases_data[9],
                'year': purchases_data[10],
                'chasis': purchases_data[11]}
    
    purchase_data = {'mileage': purchases_data[12],
                     'purchase_date': purchases_data[13],
                     'negotiated_price': purchases_data[14],
                     'bill_number': purchases_data[15],
                     'management': purchases_data[16],
                     'stock': purchases_data[17],
                     'car_color': purchases_data[18]}
    
    return client_data, car_data, purchase_data
                
    