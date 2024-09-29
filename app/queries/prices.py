from autotools.db import Database, DatabaseInstances
from autotools.db.databases import TRANSACTIONS_DATABASE
from autotools.db.tables import Cardealership

def get_prices(purchase_id):
    query = f"""SELECT price, datetime 
                FROM {Cardealership.PRICES}
                WHERE purchase_id = %s
                ORDER BY datetime DESC"""
                
    auto_db = Database(TRANSACTIONS_DATABASE, source=DatabaseInstances.AUTO360)
    prices = auto_db.read_as_pd(query, params=(purchase_id,))
    auto_db.close_connection()
    
    return prices