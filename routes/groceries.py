from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite

bp = Blueprint("groceries", __name__, url_prefix="/groceries")

@bp.route("/<action>", methods=["GET", "POST"])
def groceries_action(action):
    if action == "view":
        groceries = sqlite.fetch_all_groceries_with_names()
        print(groceries)
        return render_template("groceries.html", groceries=groceries)

    elif action == "add":
        ingredients_from_recipe = request.form.getlist("ingredients")
        if ingredients_from_recipe:
            inventory_items = sqlite.fetch_all_inventory()
            # Create a list of lowercase inventory names for easy checking
            inventory_names = [item[4].lower() for item in inventory_items]
            
            ingredients_to_add = []
            skipped_items = []

            for ingredient in ingredients_from_recipe:
                found_in_inventory = any(inv_name in ingredient.lower() for inv_name in inventory_names)
                if not found_in_inventory:
                    ingredients_to_add.append(ingredient)
                else:
                    skipped_items.append(ingredient)

            if ingredients_to_add:
                sqlite.add_grocery_item(ingredients_to_add)
                flash(f"Added {len(ingredients_to_add)} items to your shopping list.", "success")
            
            if skipped_items:
                flash(f"Skipped {len(skipped_items)} items already in your inventory.", "info")
            elif not ingredients_to_add:
                flash("All recipe ingredients are already in your inventory!", "info")
        else:
            flash("No ingredients selected to add.", "error")

    elif action == "toggle":
        item_id = request.values.get("item_id", type=int)
        if item_id is not None:
            sqlite.toggle_grocery_check(item_id)

    elif action == "remove":
        item_id = request.values.get("item_id", type=int)
        if item_id is not None:
            sqlite.remove_grocery_item(item_id)

    elif action == "update":
        item_id = request.values.get("item_id", type=int)
        new_name = request.form.get("new_name", "").strip()
        if item_id is not None:
            if new_name:
                sqlite.update_grocery_item(item_id, new_name)
                flash("Item updated successfully.", "success")
            else:
                flash("Item name cannot be empty.", "error")

    elif action == "update-all":
        for key, new_name in request.form.items():
            if key.startswith("name-"):
                item_id = key.split("-")[1]
                if new_name.strip():
                    sqlite.update_grocery_item(item_id, new_name.strip())
        flash("Shopping list updated successfully.", "success")

    elif action == "clear-checked":
        sqlite.clear_grocery_checked()
        flash("Cleared all checked items from your shopping list.", "success")

    else:
        flash("Invalid action.", "error")

    if action != "view":
        return redirect(url_for('groceries_action', action="view"))