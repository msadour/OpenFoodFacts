

class User:

    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.products = []

    def add_product(self, product):
        self.products.append(product)