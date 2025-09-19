import sqlite3
from sqlite3 import Error


def create_table_recipies():
	try:
		conn = sqlite3.connect("database.db")
		c = conn.cursor()
		c.execute(f'CREATE TABLE IF NOT EXISTS recipies(id INTEGER PRIMARY KEY, name TEXT UNIQUE, description TEXT, ingredients TEXT, instructions TEXT, image_url TEXT)')
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

def open(recipie):
	"""
    Fetches a single recipe from the database by its name.
    Uses a parameterized query to prevent SQL injection.
    """
	try:
		print(f"opening {recipie}")
		conn = sqlite3.connect("database.db")
		c = conn.cursor()
		c.execute("SELECT * from recipies WHERE name = ?", (recipie,))
		return(c.fetchone())
	except Error as e:
		print(e)
	finally:
		if conn:
			conn.close()

def get_all_recipes():
	"""Fetches the name and description of all recipes."""
	try:
		conn = sqlite3.connect("database.db")
		c = conn.cursor()
		c.execute("SELECT name, description from recipies ORDER BY name")
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
            INSERT OR IGNORE INTO recipies (name, description, image_url, ingredients, instructions)
            VALUES (?, ?, ?, ?, ?)
        """, (name, description, image_url, ingredients_json, instructions_json))
		conn.commit()
		print(f"Attempted to add recipe: {name}")
	except Error as e:
		print(e)
	finally:
		if conn:
			conn.close()

create_table_recipies()
create_table_inventory()