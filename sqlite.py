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
		c.execute(f'CREATE TABLE IF NOT EXISTS inventory(id INTEGER PRIMARY KEY, type TEXT, quantity REAL, code REAL, name TEXT, brand TEXT, single_quantity REAL, unit TEXT)')
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
		print(f"Added {name} to recipies")
	except Error as e:
		print(e)
	finally:
		if conn:
			conn.close()

def add_ingredient(quantity, code, product_name, brand, single_quantity, product_quantity_unit):
	try:
		conn = sqlite3.connect("database.db")
		c = conn.cursor()
		c.execute("""
            INSERT OR IGNORE INTO inventory (type, quantity, code, name, brand, single_quantity, unit)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("ingredient", quantity, code, product_name, brand, single_quantity, product_quantity_unit))
		conn.commit()
		print(f"Added {product_name} to inventory")
	except Error as e:
		print(e)
	finally:
		if conn:
			conn.close()

create_table_recipes()
create_table_inventory()