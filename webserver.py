from flask import Flask, request, render_template, abort, redirect, url_for, flash
import sqlite
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

@app.route("/recipe/<recipe_name>")
def recipe(recipe_name):
    recipe_data = sqlite.open(recipe_name)
    if recipe_data is None:
        abort(404)
    # The data is a tuple, e.g., (id, name, desc, ingredients_json, instructions_json, image_url)
    full_recipe = {
        "name": recipe_data[1],
        "description": recipe_data[2],
        "ingredients": json.loads(recipe_data[3]),
        "instructions": json.loads(recipe_data[4]),
        "image_url": recipe_data[5]
    }
    return render_template("recipe.html", recipe=full_recipe)

@app.route("/cookbook")
def cookbook():
    all_recipes = sqlite.get_all_recipes()
    return render_template("cookbook.html", recipes=all_recipes)

@app.route("/pantry")
def pantry():
    inventory_items = sqlite.get_all_inventory()
    return render_template("pantry.html", items=inventory_items)

@app.route("/pantry/add", methods=["POST"])
def add_item():
    name = request.form.get("name")
    quantity = request.form.get("quantity")
    unit = request.form.get("unit")
    if name and quantity and unit:
        sqlite.add_inventory_item(name, quantity, unit)
    return redirect(url_for('pantry'))

@app.route("/pantry/remove/<int:item_id>")
def remove_item(item_id):
    sqlite.remove_inventory_item(item_id)
    return redirect(url_for('pantry'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', message="Sorry, the page you are looking for does not exist."), 404

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

@app.route("/healthcheck/", methods=["GET"])
def healthcheck():
    print("Healthcheck!")
    return "200", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)
