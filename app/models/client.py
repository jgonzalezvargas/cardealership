class Client():
    def __init__(self, client_id, rut= None, client_name= None, client_last_name= None, address= None, email = None, phone = None, cars = None, purchases = None, sales = None) -> None:
        self.client_id = client_id
        self.rut = rut
        self.client_name = client_name
        self.client_last_name = client_last_name
        self.address = address
        self.email = email
        self.phone = phone
        self.cars = cars
        self.purchases = purchases
        self.sales = sales
        
        