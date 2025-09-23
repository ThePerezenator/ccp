import sqlite3
import sqlite # Import the sqlite module to run the table creation logic
import json

def seed_database():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Clear existing recipes to avoid duplicates
    c.execute("DELETE FROM recipes")
    print("Cleared existing recipes.")

    recipes_to_add = [
        {
            "name": "Chicken and Rice",
            "description": "A simple and delicious one-pan meal, perfect for a weeknight dinner.",
            "image_url": "https://i.imgur.com/s4T053A.png",
            "ingredients": {
                "Main": [
                    "1 lb chicken thighs, boneless, skinless",
                    "1 cup long-grain white rice",
                    "2 cups chicken broth",
                    "1 onion, chopped",
                    "2 cloves garlic, minced",
                    "1 tbsp olive oil"
                ],
                "Seasoning": [
                    "1 tsp paprika",
                    "1/2 tsp cumin",
                    "Salt and pepper to taste"
                ]
            },
            "instructions": {
                "Preparation": [
                    "Preheat oven to 375°F (190°C).",
                    "In a small bowl, mix together paprika, cumin, salt, and pepper. Season chicken thighs on all sides."
                ],
                "Cooking": [
                    "In a large oven-safe skillet, heat olive oil over medium-high heat. Brown chicken on both sides, then remove from skillet.",
                    "Add onion and cook until softened, about 5 minutes. Add garlic and cook for 1 more minute.",
                    "Stir in the rice to coat with oil. Pour in chicken broth and bring to a simmer.",
                    "Return chicken to the skillet, placing it on top of the rice. Cover and transfer to the preheated oven.",
                    "Bake for 25-30 minutes, or until rice is cooked and chicken is done."
                ]
            }
        }
        # You can add more recipes here in the same format
    ]

    for recipe in recipes_to_add:
        c.execute("""
            INSERT INTO recipes (name, description, image_url, ingredients, instructions)
            VALUES (?, ?, ?, ?, ?)
        """, (
            recipe["name"],
            recipe["description"],
            recipe["image_url"],
            json.dumps(recipe["ingredients"]), # Convert dict to JSON string
            json.dumps(recipe["instructions"]) # Convert dict to JSON string
        ))

    conn.commit()
    conn.close()
    print(f"Successfully added {len(recipes_to_add)} recipes to the database.")

if __name__ == "__main__":
    seed_database()
