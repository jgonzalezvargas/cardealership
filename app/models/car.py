class Car():
    def __init__(self, car_id, ppu, chasis, brand, model, version, year, client_purchases = None, client_sales = None) -> None:
        self.car_id = car_id
        self.ppu = ppu
        self.chasis = chasis
        self.brand = brand
        self.model = model
        self.version = version
        self.year = year
        self.client_purchases = client_purchases
        self.client_sales = client_sales
        