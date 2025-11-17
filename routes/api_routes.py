from flask import Blueprint, request
import api
import sqlite, json

bp = Blueprint("api", __name__, url_prefix="/api")


##### TO DO: CLEAN THIS UP

@bp.route("/ingredient_info")
def ingredient_info():
    name = request.args.get("name")
    ingredient = sqlite.fetch_one("SELECT * FROM ingredients WHERE name = ?", (name,))
    if not ingredient:
        return {"items": []}

    # Parse JSON arrays
    isbns = json.loads(ingredient["codes"]) if ingredient["codes"] else []
    brands_list = json.loads(ingredient["brands"]) if ingredient["brands"] else []

    items = []
    for i, isbn in enumerate(isbns):
        brand = "Unknown"
        if i < len(brands_list):
            brand_entry = brands_list[i]
            # If brand is a comma-separated string, just take first one for display
            if isinstance(brand_entry, str):
                brand = brand_entry.split(",")[0]
            else:
                brand = str(brand_entry)
        items.append({"isbn": isbn, "brand": brand})

    return {"items": items}

@bp.route("/nutrition")
def nutrition():
    name = request.args.get("name")
    isbn = request.args.get("isbn")
    if not name or not isbn:
        return {"nutrition": {}}

    # Look up ingredient by name
    row = sqlite.fetch_one("SELECT codes, nutrition FROM ingredients WHERE name = ?", (name,))
    if not row:
        return {"nutrition": {}}

    codes = json.loads(row["codes"]) if row["codes"] else []
    nutrition_list = json.loads(row["nutrition"]) if row["nutrition"] else []

    # Find index of ISBN in codes and return corresponding nutrition object
    try:
        index = codes.index(isbn)
        nutrition_data = nutrition_list[index] if index < len(nutrition_list) else {}
        return {"nutrition": nutrition_data}
    except ValueError:
        return {"nutrition": {}}


@bp.route("/delete_brand", methods=["POST"])
def delete_brand():
    data = request.get_json()
    name = data.get("name")
    isbn = data.get("isbn")

    if not name or not isbn:
        return {"status": "error", "message": "Missing name or ISBN"}

    row = sqlite.fetch_one("SELECT codes, nutrition, brands FROM ingredients WHERE name = ?", (name,))
    if not row:
        return {"status": "error", "message": "Ingredient not found"}

    codes = json.loads(row["codes"]) if row["codes"] else []
    nutrition_list = json.loads(row["nutrition"]) if row["nutrition"] else []
    brands = json.loads(row["brands"]) if row["brands"] else []

    try:
        index = codes.index(isbn)
        # Remove the ISBN, corresponding nutrition info, and brand
        codes.pop(index)
        nutrition_list.pop(index)
        if index < len(brands):
            brands.pop(index)

        sqlite.execute(
            "UPDATE ingredients SET codes = ?, nutrition = ?, brands = ? WHERE name = ?",
            (json.dumps(codes), json.dumps(nutrition_list), json.dumps(brands), name)
        )
        return {"status": "ok"}
    except ValueError:
        return {"status": "error", "message": "ISBN not found for this ingredient"}

@bp.route("/add_isbn", methods=["POST"])
def add_isbn():
    data = request.get_json()
    name = data["name"]
    code = data["isbn"]

    nutrition_data = api.isbn_search(code)

    # Extract brands from nutrition_data
    brands_data = nutrition_data.get("brands", [])

    # Check if ingredient exists
    row = sqlite.fetch_one("SELECT codes, nutrition, brands FROM ingredients WHERE name = ?", (name,))

    if row is None:
        # Ingredient doesn't exist, create new entry with lists
        codes_list = [code]
        nutrition_list = [nutrition_data]
        brands_list = brands_data if isinstance(brands_data, list) else [brands_data]

        sqlite.execute(
            "INSERT INTO ingredients (name, brands, codes, nutrition, quantity) VALUES (?, ?, ?, ?, ?)",
            (name, json.dumps(brands_list), json.dumps(codes_list), json.dumps(nutrition_list), 0)
        )
    else:
        # Ingredient exists, append to existing lists
        existing_codes = json.loads(row["codes"]) if row["codes"] else []
        existing_nutrition = json.loads(row["nutrition"]) if row["nutrition"] else []
        existing_brands = json.loads(row["brands"]) if row["brands"] else []

        if code not in existing_codes:
            existing_codes.append(code)
        existing_nutrition.append(nutrition_data)

        # Append brands, avoid duplicates
        if isinstance(brands_data, list):
            for b in brands_data:
                if b not in existing_brands:
                    existing_brands.append(b)
        else:
            if brands_data not in existing_brands:
                existing_brands.append(brands_data)

        sqlite.execute(
            "UPDATE ingredients SET codes = ?, nutrition = ?, brands = ? WHERE name = ?",
            (json.dumps(existing_codes), json.dumps(existing_nutrition), json.dumps(existing_brands), name)
        )

    return {"status": "ok"}