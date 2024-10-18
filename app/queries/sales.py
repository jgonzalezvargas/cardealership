from autotools.db import Database, DatabaseInstances
from autotools.db.databases import TRANSACTIONS_DATABASE
from autotools.db.tables import Cardealership
from app.utilities import get_week
import sys



def query_insert_sale(user_id, client_id, car_id, sale_date, sale_price, real_cost, source, credit_comission, card, credit, car_as_payment, mileage, car_color):
    insert_purchase_query = f"""INSERT INTO {Cardealership.SALES} (sale_date, dhv, week, mileage, car_color, source_id, credit_comission, credit, 
                                                            card, car_as_payment, sale_price, real_cost, real_margin, vendor_id, car_id, client_id) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING sale_id"""

    #print(insert_price_query%(purchase_id, user_id, car_price), file=sys.stderr)
    
    #TODO add created date to car, calculate dhv (days(sale_date - car.created_date))
    dhv = 3
    
    week = get_week(sale_date)
    real_margin = int(sale_price) - int(real_cost)

    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    s_id = auto_db.execute_query(insert_purchase_query, info=(sale_date, dhv, week, mileage, car_color, source, credit_comission, credit, 
                                                            card, car_as_payment, sale_price, real_cost, real_margin, user_id, car_id, client_id)).fetchone()
    sale_id = s_id[0]

    #SELECT purchase_sale_id
    #TODO This can be improved so much
    #CONSTRAINT: The same car can't have more than one entry in purchase_sale_id without completion
    select_purchase_sale_id_query = f"""SELECT purchase_sale_id, purchase_id FROM {Cardealership.PURCHASE_SALE} WHERE car_id = %s AND purchase_id IS NOT NULL AND sale_id IS NULL LIMIT 1"""
    ps_id = auto_db.execute_query(select_purchase_sale_id_query, info=(car_id,)).fetchone()
    if ps_id:
        purchase_sale_id = ps_id[0]
        purchase_id = ps_id[1]
        update_query = f"""UPDATE {Cardealership.PURCHASE_SALE} SET sale_id = %s, stock_id = %s WHERE purchase_sale_id = %s AND purchase_id = %s AND car_id = %s"""
        auto_db.execute_query(update_query, info=(sale_id, 5, purchase_sale_id, purchase_id, car_id))#stock_id 5 => 'Vendido'
    else:
        insert_purchase_sale_query = f"""INSERT INTO {Cardealership.PURCHASE_SALE} (purchase_id, sale_id, car_id, stock_id) VALUES (%s, %s, %s, %s)"""
        auto_db.execute_query(insert_purchase_sale_query, info=(None, sale_id, car_id, 5)) #stock_id 5 => 'Vendido'


    auto_db.close_connection()

    return sale_id




def get_sales_list():
    query = f"""SELECT s.sale_id, cl.client_id, c.car_id, u.user_id, 
                client_name, client_last_name, 
                brand, model, version, ppu,
                s.sale_date, s.mileage, s.car_color,
                s.sale_price, s.real_cost, s.real_margin,
                so.source, stock_val as stock, 
                u.name as username, u.last_name 
                FROM {Cardealership.SALES} as s
                JOIN {Cardealership.CARS} as c ON (c.car_id = s.car_id) 
                JOIN {Cardealership.CLIENTS} as cl on (s.client_id = cl.client_id) 
                JOIN {Cardealership.USERS} as u on (s.vendor_id = u.user_id) 
                JOIN {Cardealership.SALES_SOURCE} as so ON (s.source_id = so.source_id)
                JOIN {Cardealership.PURCHASE_SALE} as ps ON (s.sale_id = ps.sale_id) 
                JOIN {Cardealership.STOCK_STATUS} as ss ON (ps.stock_id = ss.stock_id) 
                GROUP BY client_name, client_last_name, s.sale_date, brand, model, version, 
                mileage, s.car_color, s.sale_price, s.real_cost, s.real_margin, 
                so.source, ss.stock_val, u.name, u.last_name, cl.client_id, 
                c.car_id, u.user_id, s.sale_id 
                ORDER BY sale_date DESC"""
                
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    sales_data = auto_db.read_as_pd(query)
    auto_db.close_connection()
    
    return sales_data


def get_sale(sale_id):
    query = f"""SELECT cl.client_id, c.car_id,
                client_name, client_last_name, rut, cl.phone,
                brand, model, version, ppu, year, chasis,
                s.sale_date, s.dhv, s.week, s.mileage, s.car_color,
                s.sale_price, s.real_cost, s.real_margin,
                so.source, stock_val as stock, 
                credit_comission, credit, card, car_as_payment,
                u.name as username, u.last_name, u.user_id
                FROM {Cardealership.SALES} as s
                JOIN {Cardealership.CARS} as c ON (c.car_id = s.car_id) 
                JOIN {Cardealership.CLIENTS} as cl on (s.client_id = cl.client_id) 
                JOIN {Cardealership.USERS} as u on (s.vendor_id = u.user_id) 
                JOIN {Cardealership.SALES_SOURCE} as so ON (s.source_id = so.source_id)
                JOIN {Cardealership.PURCHASE_SALE} as ps ON (s.sale_id = ps.sale_id) 
                JOIN {Cardealership.STOCK_STATUS} as ss ON (ps.stock_id = ss.stock_id) 
                WHERE s.sale_id = %s LIMIT 1"""
                
    #TODO Maybe reorder the JOINS
    print(query%(sale_id,), sys.stderr)
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    sale_data = auto_db.execute_query(query, info=(sale_id,)).fetchone()
    auto_db.close_connection()
    
    client_data = {'client_id': sale_data[0],
                   'client_name': sale_data[2],
                   'client_last_name': sale_data[3],
                   'rut': sale_data[4],
                   'phone': sale_data[5],
                   }
    
    car_data = {'car_id': sale_data[1],
                'brand': sale_data[6],
                'model': sale_data[7],
                'version': sale_data[8],
                'ppu': sale_data[9],
                'year': sale_data[10],
                'chasis': sale_data[11]}
    
    sale_data = {'sale_date': sale_data[12],
                'dhv': sale_data[13],
                'week': sale_data[14],
                'mileage': sale_data[15],
                'car_color': sale_data[16],
                'sale_price': sale_data[17],
                'real_cost': sale_data[18],
                'real_margin': sale_data[19],
                'source': sale_data[20],
                'stock_val': sale_data[21],
                'credit_comission': sale_data[22],
                'credit': sale_data[23],
                'card': sale_data[24],
                'car_as_payment': sale_data[25],
                'vendor': sale_data[26] + sale_data[27],
                'vendor_id': sale_data[28]}
    
    
    return client_data, car_data, sale_data