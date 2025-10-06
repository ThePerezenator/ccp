import openfoodfacts
import requests

def get_product_data(barcode):
    # Set a User-Agent, as recommended by the OFF API documentation.
    # Replace 'MyRecipeApp' with your actual application name.
    headers = {'User-Agent': 'MyRecipeApp/1.0 (contact@your-website.com)'}
    
    # The official API endpoint for getting product by barcode
    api_url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}"
    
    try:
        # Make the GET request to the Open Food Facts API
        response = requests.get(api_url, headers=headers, timeout=5)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        
        # The 'product' key contains the main data. If not found, status is 0.
        if data.get('status') == 1 and 'product' in data:
            product = data['product']
            return {
                "name": product.get('product_name', 'N/A'),
                "brands": product.get('brands', 'N/A'),
                "ingredients": product.get('ingredients_text', 'No ingredients listed'),
                "nutriscore": product.get('nutriscore_grade', 'N/A'),
                "image_url": product.get('image_front_url')
            }
        else:
            return None # Product not found
            
    except requests.exceptions.RequestException as e:
        print(f"API Error for barcode {barcode}: {e}")
        return None