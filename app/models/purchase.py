class Purchase():
    def __init__(self, purchase_id, user=None, client=None, car=None, mileage= None, purchase_date = None, car_price = None, negotiated_price = None, management = None, stock = None, bill_number = None, prices = None, car_color = None) -> None:
        self.user = user
        self.purchase_id = purchase_id
        self.client = client
        self.car = car

        self.mileage = mileage
        self.purchase_date = purchase_date
        self.price = car_price
        self.negotiated_price = negotiated_price
        self.management = management
        self.stock = stock
        self.bill_number = bill_number
        self.prices = prices
        self.car_color = car_color
        
        