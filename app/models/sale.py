class Sale():
    def __init__(self, sale_id, user = None, client = None, car = None, dhv = None, week = None, 
                 sale_date = None, sale_price = None, real_cost = None, real_margin = None, card = None,
                 source = None, stock = None, credit_comission = None, credit = None, car_as_payment = None, mileage = None, car_color = None):
        self.sale_id = sale_id
        self.user = user
        self.client = client
        self.car = car

        self.sale_date = sale_date
        self.sale_price = sale_price
        self.real_cost = real_cost
        self.source = source
        self.credit_comission = credit_comission
        self.credit = credit
        self.car_as_payment = car_as_payment
        self.mileage = mileage
        self.car_color = car_color
        self.stock = stock
        self.dhv = dhv
        self.week = week
        self.real_margin = real_margin
        self.card = card