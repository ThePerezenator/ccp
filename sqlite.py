import sqlite3
import json
from sqlite3 import Error

### RECIPIES

def fetch_all_recipes():
    return fetch_all("SELECT * FROM recipes")

def fetch_one_recipe(recipe_name):
    return fetch_one("SELECT * FROM recipes WHERE name = ?", (recipe_name,))

def update_recipe(old_name, new_name, description, instructions_json, notes):
    """
    Updates an existing recipe identified by old_name.
    Only updates the fields provided by the edit form.
    """
    execute(
        "UPDATE recipes SET name = ?, description = ?, instructions = ?, notes = ? WHERE name = ?",
        (new_name, description, instructions_json, notes, old_name)
    )

def fetch_recipes_ingredients(recipe_row):
    return fetch_all("""
            SELECT ingredients.name, ingredients.id, recipesingredients.quantity, recipesingredients.unit
            FROM recipesingredients
            JOIN ingredients ON recipesingredients.ingredientID = ingredients.id
            WHERE recipesingredients.recipeID = ?
        """, (recipe_row["id"],))

def add_recipe(name, description, image, ingredients_json, instructions_json, notes):
    """
    Adds a new recipe to the recipes table.
    """
    execute(
        "INSERT INTO recipes (name, description, image, instructions, notes) VALUES (?, ?, ?, ?, ?)",
        (name, description, image, instructions_json, notes)
    )

def delete_recipe(name):
    """
    Deletes a recipe from the database by name.
    """
    execute("DELETE FROM recipes WHERE name = ?", (name,))

### INVENTORY

def fetch_all_inventory():
	return fetch_all("SELECT * FROM ingredients")

def fetch_all_inventory_names():
    return [row[0] for row in fetch_all("SELECT name FROM ingredients")]

def get_inventory_item_by_id(item_id):
    return fetch_one("SELECT * FROM ingredients WHERE id = ?", (item_id,))

def update_inventory_quantity(item_id, new_quantity):
    execute("UPDATE ingredients SET quantity = ? WHERE id = ?", (new_quantity, item_id))

def remove_inventory_item(item_id):
    execute("DELETE FROM ingredients WHERE id = ?", (item_id,))

def add_inventory_item(quantity, name, brands, codes, nutrition):
    brands = brands if brands else None
    codes = codes if codes else None
    nutrition = nutrition if nutrition else None
    execute("INSERT INTO ingredients (name, brands, codes, nutrition, quantity) VALUES (?, ?, ?, ?, ?)",
            (name, json.dumps(brands), json.dumps(codes), json.dumps(nutrition), quantity))

### GROCERIES

def fetch_all_groceries():
	item =  fetch_all("SELECT * FROM groceries")
	print(item)
	return item

def fetch_all_groceries_with_names():
    query = """
        SELECT groceries.id,
               groceries.ingredientID,
               ingredients.name,
               groceries.quantity,
               groceries.checked
        FROM groceries
        JOIN ingredients ON groceries.ingredientID = ingredients.id
    """
    return fetch_all(query)

def add_grocery_item(items):
    for item in items:
        ingredient = fetch_one("SELECT id FROM ingredients WHERE name = ?", (item,))
        if ingredient is None:
            execute("INSERT INTO ingredients (name) VALUES (?)", (item,))
            ingredient = fetch_one("SELECT id FROM ingredients WHERE name = ?", (item,))
        ingredient_id = ingredient[0]
        # Check if grocery item already exists
        grocery = fetch_one("SELECT id FROM groceries WHERE ingredientID = ?", (ingredient_id,))
        if grocery is None:
            execute("INSERT INTO groceries (ingredientID, quantity, checked) VALUES (?, ?, ?)", (ingredient_id, 1, 0))

def remove_grocery_item(item_id):
    execute("DELETE FROM groceries WHERE id = ?", (item_id,))

def update_grocery_item(item_id, new_name):
    grocery = fetch_one("SELECT ingredientID FROM groceries WHERE id = ?", (item_id,))
    if grocery:
        ingredient_id = grocery[0]
        execute("UPDATE ingredients SET name = ? WHERE id = ?", (new_name, ingredient_id))

def toggle_grocery_check(grocery_id):
    grocery = fetch_one("SELECT checked FROM groceries WHERE id = ?", (grocery_id,))
    if grocery is not None:
        current = grocery["checked"]
        new_value = 0 if current else 1
        execute("UPDATE groceries SET checked = ? WHERE id = ?", (new_value, grocery_id))
		
def clear_grocery_checked():
    execute("DELETE FROM groceries where checked = 1")        




### SQLITE EXECUTION

def get_connection():
    return sqlite3.connect("database.db")

def fetch_all(query, params=()):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(query, params)
        return c.fetchall()
	
def fetch_one(query, params=()):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(query, params)
        return c.fetchone()

def execute(query, params=()):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(query, params)
        conn.commit()

def create_recipes():
	try:
		with get_connection() as conn:
			c = conn.cursor()
			c.execute("""CREATE TABLE IF NOT EXISTS recipes(
				id INTEGER PRIMARY KEY, 
				name TEXT UNIQUE NOT NULL, 
				description TEXT, 
				servings INTEGER, 
				instructions TEXT, 
				image TEXT, 
				notes TEXT)""")
			print(f"database CREATED")
	except Error as e:
		print(e)
	finally:
		if conn:
			conn.close()

def create_ingredients():
	try:
		with get_connection() as conn:
			c = conn.cursor()
			c.execute("""CREATE TABLE IF NOT EXISTS ingredients(
				id INTEGER PRIMARY KEY, 
				name TEXT UNIQUE NOT NULL, 
				brands TEXT, 
				codes TEXT, 
				nutrition TEXT, 
				quantity INTEGER NOT NULL)""")
			print(f"database CREATED")
	except Error as e:
		print(e)
	finally:
		if conn:
			conn.close()

def create_recipesingredients():
	try:
		with get_connection() as conn:
			c = conn.cursor()
			c.execute("""CREATE TABLE IF NOT EXISTS recipesingredients(
				id INTEGER PRIMARY KEY, 
				recipeID INTEGER NOT NULL, 
				ingredientID INTEGER NOT NULL, 
				quantity REAL NOT NULL,
                unit TEXT,
                preperation TEXT,
				FOREIGN KEY(recipeID) REFERENCES recipes(id),
				FOREIGN KEY(ingredientID) REFERENCES ingredients(id))""")
			print(f"database CREATED")
	except Error as e:
		print(e)
	finally:
		if conn:
			conn.close()

def create_groceries():
	try:
		with get_connection() as conn:
			c = conn.cursor()
			c.execute("""CREATE TABLE IF NOT EXISTS groceries(
				id INTEGER PRIMARY KEY, 
				ingredientID INTEGER NOT NULL, 
				quantity INTEGER NOT NULL, 
				checked INTEGER NOT NULL,
			 	FOREIGN KEY(ingredientID) REFERENCES ingredients(id))""")
			print(f"database CREATED")
	except Error as e:
		print(e)
	finally:
		if conn:
			conn.close()

def create_sample_data():
    # Sample ingredients
    execute("INSERT INTO ingredients (name, brands, codes, nutrition, quantity) VALUES (?, ?, ?, ?, ?)",
            ("Milk", json.dumps(["GreatValue", "Publix"]), json.dumps([111, 112]), json.dumps({"calories": 100}), 2))
    execute("INSERT INTO ingredients (name, brands, codes, nutrition, quantity) VALUES (?, ?, ?, ?, ?)",
            ("Eggs", json.dumps(["Eggland's Best"]), json.dumps([221]), json.dumps({"calories": 70}), 12))
    execute("INSERT INTO ingredients (name, brands, codes, nutrition, quantity) VALUES (?, ?, ?, ?, ?)",
            ("Flour", json.dumps(["King Arthur"]), json.dumps([331]), json.dumps({"calories": 110}), 1))

    # Sample recipes
    execute("INSERT INTO recipes (name, description, servings, instructions, image, notes) VALUES (?, ?, ?, ?, ?, ?)",
            ("Pancakes", "Fluffy breakfast pancakes", 4, """{"Instructions": ["Preheat the oven to 325\u00b0F. Lightly spray an 8x8 baking dish (not a 9x9 dish or your brownies will overcook) with cooking spray and line it with parchment paper. Spray the parchment paper.", "In a medium bowl, combine the sugar, flour, cocoa powder, powdered sugar, chocolate chips, and salt.", "In a large bowl, whisk together the eggs, olive oil, water, and vanilla.", "Sprinkle the dry mix over the wet mix and stir until just combined.", "Pour the batter into the prepared pan (it'll be thick - that's ok) and use a spatula to smooth the top. Bake for 40 to 48 minutes, or until a toothpick comes out with only a few crumbs attached (note: it's better to pull the brownies out early than to leave them in too long). Cool completely before slicing.*** Store in an airtight container at room temperature for up to 3 days. These also freeze well!", "new instructions", "sd"]}""", "", ""))
    execute("INSERT INTO recipes (name, description, servings, instructions, image, notes) VALUES (?, ?, ?, ?, ?, ?)",
            ("Scrambled Eggs", "Simple scrambled eggs", 2, """{"Instructions": ["Cut chicken in to small chunks", "Season Chicken to liking", "Heat the pan used to cook chicken and add a little bit of cooking oil", "Cook the chicken and heat the pan used to toast the tortillas and melt some butter", "Move chicken to other pan with tortilla and add cheese, fold and cook", "enjoy"]}""", "", ""))

    # Sample recipesingredients links
    execute("INSERT INTO recipesingredients (recipeID, ingredientID, servings) VALUES (?, ?, ?)",
            (1, 1, 1))  # Pancakes -> Milk
    execute("INSERT INTO recipesingredients (recipeID, ingredientID, servings) VALUES (?, ?, ?)",
            (1, 3, 1))  # Pancakes -> Flour
    execute("INSERT INTO recipesingredients (recipeID, ingredientID, servings) VALUES (?, ?, ?)",
            (2, 2, 2))  # Scrambled Eggs -> Eggs

    # Sample groceries
    execute("INSERT INTO groceries (ingredientID, quantity, checked) VALUES (?, ?, ?)",
            (1, 1, 0))
    execute("INSERT INTO groceries (ingredientID, quantity, checked) VALUES (?, ?, ?)",
            (3, 2, 0))


create_recipes()
create_ingredients()
create_recipesingredients()
create_groceries()
#create_sample_data()