import sqlite3
import json
from sqlite3 import Error


def create_table_recipes():
	try:
		conn = sqlite3.connect("database.db")
		c = conn.cursor()
		c.execute(f'CREATE TABLE IF NOT EXISTS recipes(id INTEGER PRIMARY KEY, name TEXT UNIQUE, description TEXT, ingredients TEXT, instructions TEXT, image_url TEXT)')
		print(f"database CREATED")
	except Error as e:
		print(e)
	finally:
		if conn:
			conn.close()

def create_table_inventory():
	try:
		conn = sqlite3.connect("database.db")
		c = conn.cursor()
		# Using INTEGER PRIMARY KEY makes it an auto-incrementing field
		c.execute(f'CREATE TABLE IF NOT EXISTS inventory(id INTEGER PRIMARY KEY, name TEXT, quantity REAL, unit TEXT)')
		print(f"inventory table CREATED")
	except Error as e:
		print(e)
	finally:
		if conn:
			conn.close()

def open(recipe_name):
	"""
    Fetches a single recipe from the database by its name.
    Uses a parameterized query to prevent SQL injection.
    """
	try:
		print(f"opening {recipe_name}")
		conn = sqlite3.connect("database.db")
		c = conn.cursor()
		c.execute("SELECT * from recipes WHERE name = ?", (recipe_name,))
		return(c.fetchone())
	except Error as e:
		print(e)
	finally:
		if conn:
			conn.close()

def get_all_recipes():
	"""Fetches the name, description, and image URL of all recipes."""
	try:
		conn = sqlite3.connect("database.db")
		c = conn.cursor()
		c.execute("SELECT name, description, image_url from recipes ORDER BY name")
		return c.fetchall()
	except Error as e:
		print(e)
	finally:
		if conn:
			conn.close()

def get_all_inventory():
	"""Fetches all items from the inventory."""
	try:
		conn = sqlite3.connect("database.db")
		c = conn.cursor()
		c.execute("SELECT * from inventory ORDER BY name")
		return c.fetchall()
	except Error as e:
		print(e)
	finally:
		if conn:
			conn.close()

def add_inventory_item(name, quantity, unit):
	"""Adds a new item to the inventory."""
	try:
		conn = sqlite3.connect("database.db")
		c = conn.cursor()
		c.execute("INSERT INTO inventory (name, quantity, unit) VALUES (?, ?, ?)", (name, quantity, unit))
		conn.commit()
	except Error as e:
		print(e)
	finally:
		if conn:
			conn.close()

def remove_inventory_item(item_id):
	"""Removes an item from the inventory by its ID."""
	try:
		conn = sqlite3.connect("database.db")
		c = conn.cursor()
		c.execute("DELETE from inventory WHERE id = ?", (item_id,))
		conn.commit()
	except Error as e:
		print(e)
	finally:
		if conn:
			conn.close()

def add_recipe(name, description, image_url, ingredients_json, instructions_json):
	"""Adds a new recipe to the database. Uses INSERT OR IGNORE to prevent errors on duplicate names."""
	try:
		conn = sqlite3.connect("database.db")
		c = conn.cursor()
		c.execute("""
            INSERT OR IGNORE INTO recipes (name, description, image_url, ingredients, instructions)
            VALUES (?, ?, ?, ?, ?)
        """, (name, description, image_url, ingredients_json, instructions_json))
		conn.commit()
		print(f"Attempted to add recipe: {name}")
	except Error as e:
		print(e)
	finally:
		if conn:
			conn.close()

def seed_database():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Clear existing recipes to avoid duplicates
    c.execute("DELETE FROM recipes")
    print("Cleared existing recipes.")

    recipes_to_add = [
        {
            "name": "Chicken and Rice",
            "description": "A simple and delicious one-pan meal, perfect for a weeknight dinner.",
            "image_url": "https://i.imgur.com/s4T053A.png",
            "ingredients": {
                "Main": [
                    "1 lb chicken thighs, boneless, skinless",
                    "1 cup long-grain white rice",
                    "2 cups chicken broth",
                    "1 onion, chopped",
                    "2 cloves garlic, minced",
                    "1 tbsp olive oil"
                ],
                "Seasoning": [
                    "1 tsp paprika",
                    "1/2 tsp cumin",
                    "Salt and pepper to taste"
                ]
            },
            "instructions": {
                "Preparation": [
                    "Preheat oven to 375°F (190°C).",
                    "In a small bowl, mix together paprika, cumin, salt, and pepper. Season chicken thighs on all sides."
                ],
                "Cooking": [
                    "In a large oven-safe skillet, heat olive oil over medium-high heat. Brown chicken on both sides, then remove from skillet.",
                    "Add onion and cook until softened, about 5 minutes. Add garlic and cook for 1 more minute.",
                    "Stir in the rice to coat with oil. Pour in chicken broth and bring to a simmer.",
                    "Return chicken to the skillet, placing it on top of the rice. Cover and transfer to the preheated oven.",
                    "Bake for 25-30 minutes, or until rice is cooked and chicken is done."
                ]
            }
        }
        # You can add more recipes here in the same format
    ]

    for recipe in recipes_to_add:
        c.execute("""
            INSERT INTO recipes (name, description, image_url, ingredients, instructions)
            VALUES (?, ?, ?, ?, ?)
        """, (
            recipe["name"],
            recipe["description"],
            recipe["image_url"],
            json.dumps(recipe["ingredients"]), # Convert dict to JSON string
            json.dumps(recipe["instructions"]) # Convert dict to JSON string
        ))

    conn.commit()
    conn.close()
    print(f"Successfully added {len(recipes_to_add)} recipes to the database.")

create_table_recipes()
create_table_inventory()