class Category:

    def __init__(self, name):
        self.login = name
        self.products = []
        self.subcategorys = []

    def add_product(self, product):
        self.product.append(product)

    def add_subcategory(self, subcategory):
        self.subcategorys.append(subcategory)