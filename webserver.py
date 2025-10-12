import sqlite
import api
from flask import Flask, request, render_template, abort, redirect, url_for, flash
import json
from recipe_scrapers import scrape_me


port = "5001"

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'ucf-neptune-super-cool-156-super-secure-key-ha-69'

#dashboard
@app.route("/")
def index():
    all_recipes = sqlite.get_all_recipes()
    inventory_items = sqlite.get_all_inventory()
    return render_template("index.html", recipes=all_recipes, inventory=inventory_items)

#cookbook
@app.route("/cookbook")
def cookbook():
    all_recipes = sqlite.get_all_recipes()
    return render_template("cookbook.html", recipes=all_recipes)

#open specefic recipie
@app.route("/recipe/<recipe_name>")
def recipe(recipe_name):
    recipe_data = sqlite.open(recipe_name)
    if recipe_data is None:
        abort(404)
    full_recipe = {
        "name": recipe_data['name'],
        "description": recipe_data['description'],
        "ingredients": json.loads(recipe_data['ingredients']),
        "instructions": json.loads(recipe_data['instructions']),
        "image_url": recipe_data['image_url'],
        "notes": recipe_data['notes']
    }
    return render_template("recipe.html", recipe=full_recipe)

#edit recipe
@app.route("/recipe/<recipe_name>/edit", methods=["GET", "POST"])
def edit_recipe(recipe_name):
    if request.method == "POST":
        new_name = request.form.get("name").strip()
        if not new_name:
            flash("Recipe name is required.", "error")
            # We need to pass the unsaved data back to the template
            return render_template("edit_recipe.html", recipe=request.form)

        description = request.form.get("description")
        # Split textareas back into lists, removing any blank lines
        ingredients_list = [line.strip() for line in request.form.get("ingredients", "").split('\n') if line.strip()]
        instructions_list = [line.strip() for line in request.form.get("instructions", "").split('\n') if line.strip()]
        notes = request.form.get("notes")

        # Re-create the JSON structure. This assumes a single category.
        ingredients_json = json.dumps({"Ingredients": ingredients_list})
        instructions_json = json.dumps({"Instructions": instructions_list})
 
        sqlite.update_recipe(recipe_name, new_name, description, ingredients_json, instructions_json, notes)
        flash(f"Successfully updated '{new_name}'!", 'success')
        return redirect(url_for('recipe', recipe_name=new_name))

    # For GET request, show the edit form
    recipe_data = sqlite.open(recipe_name)
    if recipe_data is None:
        abort(404)

    # Unpack the JSON for the textareas.
    # The .get('Ingredients', []) provides a default empty list to prevent errors.
    ingredients_dict = json.loads(recipe_data['ingredients'])
    instructions_dict = json.loads(recipe_data['instructions'])

    editable_recipe = {
        "name": recipe_data['name'],
        "description": recipe_data['description'],
        "ingredients": ingredients_dict.get('Ingredients', []),
        "instructions": instructions_dict.get('Instructions', []),
        "notes": recipe_data['notes']
    }
    return render_template("edit_recipe.html", recipe=editable_recipe)

#new recipe
@app.route("/recipe/new", methods=["GET", "POST"])
def new_recipe():
    if request.method == "POST":
        name = request.form.get("name").strip()
        if not name:
            flash("Recipe name is required.", "error")
            return render_template("edit_recipe.html", recipe=request.form, is_new=True)

        if sqlite.open(name):
            flash("A recipe with this name already exists. Please choose a different name.", "error")
            return render_template("edit_recipe.html", recipe=request.form, is_new=True)

        description = request.form.get("description")
        ingredients_list = [line.strip() for line in request.form.get("ingredients", "").split('\n') if line.strip()]
        instructions_list = [line.strip() for line in request.form.get("instructions", "").split('\n') if line.strip()]
        notes = request.form.get("notes")

        ingredients_json = json.dumps({"Ingredients": ingredients_list})
        instructions_json = json.dumps({"Instructions": instructions_list})

        sqlite.add_recipe(name, description, "", ingredients_json, instructions_json, notes)
        flash(f"Successfully created '{name}'!", 'success')
        return redirect(url_for('recipe', recipe_name=name))

    # For GET request, show a blank form
    return render_template("edit_recipe.html", recipe={}, is_new=True)

#import recipe
@app.route("/import/url", methods=["POST"])
def import_url():
    url = request.form.get("recipe_url")
    if not url:
        flash("Please provide a URL.", "error")
        return redirect(url_for('index'))

    # Otherwise, treat it as a blog/recipe site
    try:
        scraper = scrape_me(url)
        
        # The instructions from the scraper are a single string, so we split it into a list
        instructions_list = [step.strip() for step in scraper.instructions().split('\n') if step.strip()]

        sqlite.add_recipe(
            scraper.title(),
            scraper.description(),
            scraper.image(),
            json.dumps({"Ingredients": scraper.ingredients()}),
            json.dumps({"Instructions": instructions_list})
        )
        flash(f"Successfully imported '{scraper.title()}'!", 'success')
        return redirect(url_for('recipe', recipe_name=scraper.title()))
    except Exception as e:
        print(f"Error scraping URL: {e}")
        flash(f"Could not import recipe from that URL. The site may not be supported.", "error")
        return redirect(url_for('index'))

#inventory
@app.route("/inventory")
def inventory():
    inventory_items = sqlite.get_all_inventory()
    return render_template("inventory.html", items=inventory_items)

@app.route("/inventory/add", methods=["POST"])
def add_item():
    name = request.form.get("name")
    quantity = request.form.get("quantity")
    unit = request.form.get("unit")
    if name and quantity and unit:
        sqlite.add_inventory_item(quantity, "", name, "", "", "")
    return redirect(url_for('inventory'))

@app.route("/inventory/remove/<int:item_id>")
def remove_item(item_id):
    sqlite.remove_inventory_item(item_id)
    return redirect(url_for('inventory'))

@app.route("/inventory/increase/<int:item_id>")
def increase_quantity(item_id):
    # This is not very efficient, but simple. A better way would be one SQL query.
    item = next((i for i in sqlite.get_all_inventory() if i[0] == item_id), None)
    if item:
        new_quantity = item[2] + 1
        sqlite.update_inventory_quantity(item_id, new_quantity)
    return redirect(url_for('inventory'))

@app.route("/inventory/decrease/<int:item_id>")
def decrease_quantity(item_id):
    item = next((i for i in sqlite.get_all_inventory() if i[0] == item_id), None)
    if item and item[2] > 1:
        sqlite.update_inventory_quantity(item_id, item[2] - 1)
    else: # If quantity is 1 or less, remove it
        sqlite.remove_inventory_item(item_id)
    return redirect(url_for('inventory'))

@app.route("/product/<code>")
def product_page(code):
    product_data = sqlite.get_inventory_item_by_code(code)
    if product_data is None:
        abort(404)
    return render_template("product.html", product=product_data)

@app.route("/product/isbn", methods=["POST"])
def product_by_isbn():
    isbn = request.form.get("isbn_code")
    if not isbn:
        flash("Please enter a barcode or ISBN.", "error")
        return redirect(url_for('inventory'))
    
    # Remove any dashes or spaces from the input
    clean_isbn = isbn.replace('-', '').replace(' ', '')
    
    product_info = api.isbn_search(clean_isbn)
    
    if product_info:
        code = product_info["code"]
        sqlite.add_ingredient(1, code, product_info["product_name"], product_info["brands"], product_info.get("product_quantity"), product_info.get("product_quantity_unit"))
        flash(f"Successfully imported '{product_info['product_name']}'!", 'success')
        return redirect(url_for('product_page', code=code))
    else:
        flash(f"Product with barcode '{isbn}' not found in Open Food Facts.", "error")
        return redirect(url_for('inventory'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', message="Sorry, the page you are looking for does not exist."), 404

@app.route("/healthcheck/", methods=["GET"])
def healthcheck():
    print("Healthcheck!")
    return "200", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)