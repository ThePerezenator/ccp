from flask import Flask, request, render_template, abort, redirect, url_for, flash
import sqlite
import json
import re
import requests
from bs4 import BeautifulSoup
from recipe_scrapers import scrape_me



app = Flask(__name__, static_folder='static')
# A secret key is required for flash messaging
app.config['SECRET_KEY'] = 'a-super-secret-key-that-you-should-change'

#main home page
@app.route("/")
def index():
    all_recipes = sqlite.get_all_recipes()
    inventory_items = sqlite.get_all_inventory()
    return render_template("index.html", recipes=all_recipes, inventory=inventory_items)

@app.route("/recipe/<recipe_name>")
def recipe(recipe_name):
    # The previous suggestion to fix the `open` function is applied here
    recipe_data = sqlite.open(recipe_name)
    if recipe_data is None:
        # abort(404) is a handy way to trigger the 404 error handler
        abort(404)
    # The data is a tuple, e.g., (id, name, desc, ingredients_json, instructions_json, image_url)
    # We parse the JSON strings into Python objects
    full_recipe = {
        "name": recipe_data[1],
        "description": recipe_data[2],
        "ingredients": json.loads(recipe_data[3]),
        "instructions": json.loads(recipe_data[4]),
        "image_url": recipe_data[5]
    }
    return render_template("recipes.html", recipe=full_recipe)

@app.route("/cookbook")
def cookbook():
    all_recipes = sqlite.get_all_recipes()
    return render_template("cookbook.html", recipes=all_recipes)

@app.route("/pantry")
def pantry():
    inventory_items = sqlite.get_all_inventory()
    return render_template("inventory.html", items=inventory_items)

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

def parse_gdoc_html(html_content):
    """
    Parses the HTML content from a Google Doc to extract recipe details.
    This is a best-effort parser and assumes a certain document structure.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Try to find title in a <p> with class 'title', then h1, then h2
    title_tag = soup.find(lambda tag: tag.name == 'p' and 'title' in tag.get('class', []))    
    if not title_tag:
        title_tag = soup.find(['h1', 'h2'])
    
    # Try to find description in a <p> with class 'subtitle'
    desc_tag = soup.find(lambda tag: tag.name == 'p' and 'subtitle' in tag.get('class', []))

    recipe = {
        "name": title_tag.get_text(strip=True) if title_tag else "Untitled Recipe",
        "description": desc_tag.get_text(strip=True) if desc_tag else "",
        "image_url": None,
        "ingredients": {},
        "instructions": {}
    }

    # A more robust way to find ingredients and instructions.
    # It finds any tag containing the keyword and then looks for the *next* list.
    ingredient_header = soup.find(lambda tag: 'ingredient' in tag.get_text(strip=True).lower())
    if ingredient_header:
        ingredient_list = ingredient_header.find_next(['ul', 'ol'])
        if ingredient_list:
            items = [li.get_text(strip=True) for li in ingredient_list.find_all('li') if li.get_text(strip=True)]
            if items:
                # Use the header's text as the category key
                recipe['ingredients'][ingredient_header.get_text(strip=True)] = items

        # Start searching for instructions *after* the ingredients list to avoid re-selecting it.
        search_area = ingredient_list or soup
        instruction_header = search_area.find(lambda tag: 'instruction' in tag.get_text(strip=True).lower() or 'method' in tag.get_text(strip=True).lower())
        if instruction_header:
            instruction_list = instruction_header.find_next(['ul', 'ol'])
            if instruction_list:
                steps = [li.get_text(strip=True) for li in instruction_list.find_all('li') if li.get_text(strip=True)]
                if steps:
                    recipe['instructions'][instruction_header.get_text(strip=True)] = steps
    else:
        # Fallback for documents that might not have an ingredients list
        instruction_header = soup.find(lambda tag: 'instruction' in tag.get_text(strip=True).lower() or 'method' in tag.get_text(strip=True).lower())

    return recipe

def handle_gdoc_import(url):
    """Handles the logic for importing a Google Doc."""
    print(f"Handling Google Doc import for: {url}")
    match = re.search(r'/document/d/([a-zA-Z0-9-_]+)', url)
    if not match:
        return "Invalid Google Doc URL", 400
    
    doc_id = match.group(1)
    export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=html"
    
    try:
        response = requests.get(export_url)
        response.raise_for_status() # Will raise an error for bad responses
        parsed_recipe = parse_gdoc_html(response.text)
        
        # Save to database
        sqlite.add_recipe(
            parsed_recipe['name'],
            parsed_recipe['description'],
            parsed_recipe['image_url'],
            json.dumps(parsed_recipe['ingredients']),
            json.dumps(parsed_recipe['instructions'])
        )
        
        flash(f"Successfully imported '{parsed_recipe['name']}'!", 'success')
        return redirect(url_for('recipe', recipe_name=parsed_recipe['name']))
    except Exception as e:
        flash(f"Error fetching Google Doc: {e}", "error")
        return redirect(url_for('index'))

@app.route("/import/url", methods=["POST"])
def import_url():
    url = request.form.get("recipe_url")
    if not url:
        flash("Please provide a URL.", "error")
        return redirect(url_for('index'))

    # Check if it's a Google Doc link
    if 'docs.google.com/document' in url:
        return handle_gdoc_import(url)

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
    app.run(host='0.0.0.0', port="5001", debug=True)
