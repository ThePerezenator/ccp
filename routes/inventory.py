from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite

bp = Blueprint("inventory", __name__, url_prefix="/inventory")

@bp.route("/<action>", methods=["GET", "POST"])
def inventory_action(action):
    item_id = request.values.get("item_id", type=int)
    name = request.values.get("name")
    quantity = request.values.get("quantity")
    unit = request.values.get("unit")

    if action == "view":
        inventory = sqlite.fetch_all_inventory()
        return render_template("inventory.html", items=inventory)

    elif action == "add":
        data = request.get_json()
        if not data:
            flash("No data received", "error")
            return redirect(url_for('inventory.inventory_action', action="view"))

        name = data.get("name", "").strip()
        quantity = data.get("quantity", "").strip()

        if not name or not quantity:
            flash("Ingredient name and quantity are required.", "error")
            return redirect(url_for('inventory.inventory_action', action="view"))

        try:
            qty_float = float(quantity)
            sqlite.execute("""INSERT INTO ingredients (name, quantity) VALUES (?, ?)""",
                                   (name, qty_float))
        except ValueError:
            flash("Quantity must be a number.", "error")

    elif action == "remove":
        if item_id:
            sqlite.execute("DELETE FROM recipesingredients WHERE ingredientID = ?", (item_id,))
            sqlite.remove_inventory_item(item_id)

    elif action == "increase":
        if item_id:
            item = sqlite.get_inventory_item_by_id(item_id)
            if item:
                new_quantity = item["quantity"] + 1
                sqlite.update_inventory_quantity(item_id, new_quantity)

    elif action == "decrease":
        if item_id:
            item = sqlite.get_inventory_item_by_id(item_id)
            if item:
                if item["quantity"] > 1:
                    sqlite.update_inventory_quantity(item_id, item["quantity"] - 1)
                else:
                    sqlite.remove_inventory_item(item_id)

    return redirect(url_for('inventory.inventory_action', action="view"))