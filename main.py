import sqlite
from flask import Flask, render_template, request
from routes import recipe, groceries, inventory, api_routes

port = "5001"

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'ucf-neptune-super-cool-156-super-secure-key-ha-69'

app.register_blueprint(recipe.bp)
app.register_blueprint(groceries.bp)
app.register_blueprint(inventory.bp)
app.register_blueprint(api_routes.bp)

@app.route("/")
def index():
    recipes = sqlite.fetch_all_recipes()
    inventory = sqlite.fetch_all_inventory()
    groceries = sqlite.fetch_all_groceries_with_names()
    return render_template("index.html", recipes=recipes, inventory=inventory, groceries=groceries)

@app.route("/cookbook")
def cookbook():
    recipes = sqlite.fetch_all_recipes()
    return render_template("cookbook.html", recipes=recipes)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', message="Sorry, the page you are looking for does not exist."), 404

@app.route("/meal_plan/")
def meal_plan():
    recipes = sqlite.fetch_all_recipes()
    return render_template("meal_plan.html", recipes=recipes), 200

@app.route("/meal_plan/add", methods=["POST"])
def meal_plan_add():
    payload = request.get_json(silent=True) or {}
    print(f"Meal plan add: {payload}")
    return {"status": "ok"}, 200

@app.route("/healthcheck/", methods=["GET"])
def healthcheck():
    print("Healthcheck!")
    return "200", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=False)