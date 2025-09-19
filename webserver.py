from flask import Flask, request, render_template, abort, redirect, url_for, current_app as app
from flask import Flask, request, render_template, abort, redirect, url_for
import sqlite
import json

port = "5001"
path = "/CCP"

app = Flask(__name__, static_folder='static')

#main home page
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/recipie/<recipie_name>")
def recipie(recipie_name):
    # The previous suggestion to fix the `open` function is applied here
    recipie_data = sqlite.open(recipie_name)
    if recipie_data is None:
        # abort(404) is a handy way to trigger the 404 error handler
        abort(404)
    # The data is a tuple, e.g., (id, name, desc, ingredients_json, instructions_json, image_url)
    # We parse the JSON strings into Python objects
    full_recipe = {
        "name": recipie_data[1],
        "description": recipie_data[2],
        "ingredients": json.loads(recipie_data[3]),
        "instructions": json.loads(recipie_data[4]),
        "image_url": recipie_data[5]
    }
    return render_template("recipies.html", recipe=full_recipe)

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


@app.route("/healthcheck/", methods=["GET"])
def healthcheck():
    print("Healthcheck!")
    return "200", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)
