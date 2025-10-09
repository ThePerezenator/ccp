import openfoodfacts
    
def isbn_search(code):
    try:
        api = openfoodfacts.API(user_agent="MyAwesomeApp/1.0")
        product = api.product.get(code, fields=["code", "status", "product_name", "brands", "product_quantity", "product_quantity_unit"])
        if product == None:
            return None
        else:
            print(product)
            return product
    except:
        print(f"Error isbn_search: {code}")
        return None
    