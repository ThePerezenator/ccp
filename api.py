from openfoodfacts import API, APIVersion, Environment, Country
    
def isbn_search(code):
    try:
        api = API(user_agent="MyAwesomeApp/1.0", version=APIVersion.v3, environment=Environment.org, country=Country.us)
        product = api.product.get(code, fields=["code", "status", "abbreviated_product_name", "product_keywords", "brands", "product_quantity", 
                                                "product_quantity_unit", "energy-kcal_serving", "energy-kcal_unit", "fat_serving", "fat_unit", "saturated-fat_serving", 
                                                "saturated-fat_unit", "carbohydrates_serving", "carbohydrates_unit", "sugars_serving", "sugars_unit", "proteins_serving", 
                                                "proteins_unit", "salt_serving", "salt_unit", "allergens"])
        if product == None:
            return None
        else:
            print(product)
            return product
    except:
        print(f"Error isbn_search: {code}")
        return None