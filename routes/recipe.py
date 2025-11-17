from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
import api
import sqlite, json

bp = Blueprint("recipe", __name__, url_prefix="/recipe")

@bp.route("/<action>", methods=["GET", "POST"])
@bp.route("/<action>/<recipe_name>", methods=["GET", "POST"])
def recipe_action(action, recipe_name=None):
    # --- VIEW RECIPE ---
    if action == "view":
        if recipe_name is None:
            abort(404)

        recipe_row = sqlite.fetch_one_recipe(recipe_name)
        if recipe_row is None:
            abort(404)

        ingredients = sqlite.fetch_recipes_ingredients(recipe_row)

        instructions = []
        if recipe_row["instructions"]:
            try:
                data = json.loads(recipe_row["instructions"])
                instructions = data.get("Instructions", [])
            except json.JSONDecodeError:
                instructions = recipe_row["instructions"].split("\n")
        print(sqlite.fetch_all_inventory_names())
        return render_template(
            "recipe.html",
            recipe=recipe_row,
            ingredients=ingredients,
            instructions=instructions,
            inventory=sqlite.fetch_all_inventory_names()
        )

    elif action == "edit":
        if recipe_name is None:
            abort(404)

        if request.method == "POST":
            data = request.get_json()
            # --- Check if this is an ingredient deletion request ---
            if "delete_ingredient" in data:
                ing_id = data["delete_ingredient"]
                recipe_row = sqlite.fetch_one_recipe(recipe_name)
                recipe_id = recipe_row["id"]
                sqlite.execute("DELETE FROM recipesingredients WHERE recipeID = ? AND ingredientID = ?", (recipe_id, ing_id))
                return {"status": "deleted"}, 200

            # --- Check if this is an ingredient addition request ---
            if 'name' in data and 'quantity' in data and 'unit' in data:
                name = data['name'].strip()
                quantity = data['quantity'].strip()
                unit = data['unit'].strip()

                if not name or not quantity:
                    return {'error': 'Missing required fields'}, 400

                recipe_row = sqlite.fetch_one_recipe(recipe_name)
                recipe_id = recipe_row["id"]

                # Check if ingredient exists
                existing = sqlite.fetch_one("SELECT id FROM ingredients WHERE name = ?", (name,))
                if existing:
                    ingredient_id = existing["id"]
                else:
                    sqlite.execute("INSERT INTO ingredients (name, brands, codes, nutrition, quantity) VALUES (?, ?, ?, ?, ?)",
                                   (name, "[]", "[]", "{}", 0))
                    ingredient_id_row = sqlite.fetch_one("SELECT id FROM ingredients WHERE name = ?", (name,))
                    ingredient_id = ingredient_id_row["id"]

                # Insert into recipesingredients
                sqlite.execute("INSERT INTO recipesingredients (recipeID, ingredientID, quantity, unit) VALUES (?, ?, ?, ?)",
                               (recipe_id, ingredient_id, quantity, unit))
                return {'status': 'ok'}, 200

            new_title = data.get("title", "").strip()
            new_description = data.get("description", "").strip()
            new_instructions = data.get("instructions", [])
            new_notes = data.get("notes", "").strip()

            instructions_json = json.dumps({"Instructions": new_instructions})

            sqlite.update_recipe(recipe_name, new_title, new_description, instructions_json, new_notes)
            return {"status": "ok"}, 200

        # If GET, load the recipe and render the editable page
        recipe_row = sqlite.fetch_one_recipe(recipe_name)
        if recipe_row is None:
            abort(404)

        ingredients = sqlite.fetch_recipes_ingredients(recipe_row)

        instructions = []
        if recipe_row["instructions"]:
            try:
                data = json.loads(recipe_row["instructions"])
                instructions = data.get("Instructions", [])
            except json.JSONDecodeError:
                instructions = recipe_row["instructions"].split("\n")

        return render_template(
            "recipe.html",
            recipe=recipe_row,
            ingredients=ingredients,
            instructions=instructions,
            inventory=sqlite.fetch_all_inventory()
        )

    # --- DELETE RECIPE ---
    elif action == "delete":
        if recipe_name is None:
            flash("Recipe not specified.", "error")
            return redirect(url_for('cookbook'))

        recipe = sqlite.fetch_one_recipe(recipe_name)
        if not recipe:
            flash("Recipe not found.", "error")
            return redirect(url_for('cookbook'))

        sqlite.execute("DELETE FROM recipesingredients WHERE recipeID = ?", (recipe["id"],))
        sqlite.delete_recipe(recipe_name)
        flash(f'Recipe "{recipe_name}" deleted successfully.', "success")
        return redirect(url_for('cookbook'))

    # --- NEW RECIPE ---
    elif action == "new":
        if request.method == "POST":
            name = request.form.get("name").strip()
            if not name:
                flash("Recipe name is required.", "error")
                return render_template("edit_recipe.html", recipe=request.form, is_new=True)

            if sqlite.fetch_one_recipe(name):
                flash("A recipe with this name already exists. Please choose a different name.", "error")
                return render_template("edit_recipe.html", recipe=request.form, is_new=True)

            description = request.form.get("description")
            ingredients_list = [line.strip() for line in request.form.get("ingredients", "").split('\n') if line.strip()]
            instructions_list = [line.strip() for line in request.form.get("instructions", "").split('\n') if line.strip()]
            notes = request.form.get("notes")

            ingredients_json = json.dumps({"Ingredients": ingredients_list})
            instructions_json = json.dumps({"Instructions": instructions_list})

            sqlite.add_recipe(name, description, "", ingredients_json, instructions_json, notes)
            flash(f"Successfully created '{name}'!", "success")
            return redirect(url_for("recipe.recipe_action", action="view", recipe_name=name))

        return render_template("edit_recipe.html", recipe={}, is_new=True)

    if action == "import":
        if request.method == "POST":
            url = request.form.get("recipe_url")
            if not url:
                flash("Please provide a URL.", "error")
                return redirect(url_for('index'))

            try:
                recipe_name_from_url = api.scrape_recipe(url)
                # Redirect to edit page for the imported recipe
                return redirect(url_for('recipe.recipe_action', action="edit", recipe_name=recipe_name_from_url))
            except Exception as e:
                print(f"Error scraping URL: {e}")
                flash(f"Could not import recipe from that URL. The site may not be supported.", "error")
                return redirect(url_for('index'))

    # --- INVALID ACTION ---
    else:
        flash("Invalid recipe action.", "error")
        abort(404)