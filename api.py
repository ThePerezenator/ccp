from openfoodfacts import API, APIVersion, Environment, Country
from recipe_scrapers import scrape_me
import json
from ingredient_parser import parse_ingredient
from recipe_scrapers import scrape_me
import unicodedata
import re
import sqlite
from fractions import Fraction

def isbn_search(code):
    try:
        api = API(user_agent="CCP", version=APIVersion.v3, environment=Environment.org, country=Country.us)
        product = api.product.get(code, fields=["code", "status", "product_name", "product_keywords", "brands", "product_quantity", 
                                                "product_quantity_unit", "energy-kcal_serving", "energy-kcal_unit", "fat_serving", "fat_unit", "saturated-fat_serving", 
                                                "saturated-fat_unit", "carbohydrates_serving", "carbohydrates_unit", "sugars_serving", "sugars_unit", "proteins_serving", 
                                                "proteins_unit", "salt_serving", "salt_unit", "allergens"])
        if product == None:
            return None
        else:
            return product
    except:
        print(f"Error isbn_search: {code}")
        return None
    

def scrape_recipe(url):
    scraper = scrape_me(url)

    title = scraper.title()
    description = scraper.description()
    image = scraper.image()

    cleaned_ingredients = [clean_text(ing) for ing in scraper.ingredients()]

    instructions_list = [step.strip() for step in scraper.instructions().split('\n') if step.strip()]
    instructions_json = json.dumps({"Instructions": instructions_list})

    sqlite.execute(
        "INSERT INTO recipes (name, description, instructions, image, notes) VALUES (?, ?, ?, ?, ?)",
        (title, description, instructions_json, image, "")
    )
    recipe_id = sqlite.fetch_one("SELECT id FROM recipes WHERE name = ?", (title,))["id"]

    # Process ingredients
    for ingredient_text in cleaned_ingredients:
        parsed = parse_ingredient(ingredient_text)

        # Extract ingredient name
        if parsed.name:
            name = parsed.name[0].text
        else:
            name = ingredient_text  # fallback to raw text if parser fails

        # Default quantity/unit if parsing fails
        quantity = 0
        unit = ""

        # Extract quantity and unit if available
        if parsed.amount:
            try:
                quantity = float(Fraction(parsed.amount[0].quantity)) if parsed.amount[0].quantity else 0
            except ValueError:
                quantity = 0
            # Convert the unit object to string
            unit = str(parsed.amount[0].unit) if parsed.amount[0].unit else ""

        # Check if ingredient already exists in database
        existing = sqlite.fetch_one("SELECT id FROM ingredients WHERE name = ?", (name,))
        if existing is None:
            # Insert new ingredient with default quantity 0
            sqlite.execute("INSERT INTO ingredients (name, quantity) VALUES (?, ?)", (name, 0))
            ingredient_id = sqlite.fetch_one("SELECT id FROM ingredients WHERE name = ?", (name,))["id"]
            print(f"Added new ingredient to database: {name}")
        else:
            ingredient_id = existing["id"]
            print(f"Ingredient already exists: {name}")

        # Link ingredient to recipe in recipesingredients
        prep = parsed.preparation.text if parsed.preparation else ""
        existing_link = sqlite.fetch_one(
            "SELECT id FROM recipesingredients WHERE recipeID = ? AND ingredientID = ?",
            (recipe_id, ingredient_id)
        )
        if existing_link is None:
            sqlite.execute(
                "INSERT INTO recipesingredients (recipeID, ingredientID, quantity, unit, preperation) VALUES (?, ?, ?, ?, ?)",
                (recipe_id, ingredient_id, quantity, unit, prep)
            )
            print(f"Linked {name} to recipe {title} with {quantity} {unit}")
        else:
            print(f"{name} already linked to recipe {title}")    
    return scraper.title()


def clean_text(text):
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    # Remove unusual characters like "▢"
    text = re.sub(r'[^\w\s\.,/-]', '', text)
    # Strip extra whitespace
    text = text.strip()
    return text