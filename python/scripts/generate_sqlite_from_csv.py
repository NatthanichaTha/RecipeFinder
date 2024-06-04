import pandas as pd
import sqlite3
import ast

con = sqlite3.connect("recipe.db")

def init_db():
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS recipes(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                minutes INTEGER,
                calories INTEGER,
                total_fat INTEGER,
                sugar INTEGER,
                sodium INTEGER,
                protein INTEGER,
                saturated_fat INTEGER,
                carbohydrates INTEGER
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS ingredients(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS recipe_ingredients(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER,
                ingredient_id INTEGER,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id),
                FOREIGN KEY (ingredient_id) REFERENCES ingredients (id)
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS recipe_steps(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER,
                step_no INTEGER,
                step TEXT,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id)
    )""")

    con.commit()

df = pd.read_csv("RAW_recipes.csv")
df = df.drop(columns=["id", "contributor_id", "submitted", "tags"])
df = df.dropna()


def insert_ingredient(ingredient):
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO ingredients (name) VALUES (?)", [ingredient])
        con.commit()
        return cur.lastrowid
    except Exception as e:
        cur.execute("SELECT id FROM ingredients WHERE name = ?", [ingredient])
        res = cur.fetchone()
        return res[0]
    
def insert_recipe(recipe):
    cur = con.cursor()
    nutri = ast.literal_eval(recipe["nutrition"])
    cur.execute("INSERT INTO recipes (name, description, minutes, calories, total_fat, sugar, sodium, protein, saturated_fat, carbohydrates) VALUES (?,?,?,?,?,?,?,?,?,?)", [recipe["name"], recipe["description"], recipe["minutes"], nutri[0], nutri[1], nutri[2], nutri[3], nutri[4], nutri[5], nutri[6]])
    return cur.lastrowid

def insert_recipe_ingredient(recipe_id, ingredient_id):
    cur = con.cursor()
    cur.execute("INSERT INTO recipe_ingredients (recipe_id, ingredient_id) VALUES (?, ?)", [recipe_id, ingredient_id])
    con.commit()

def insert_recipe_step(recipe_id: int, step_no: int, step: str):
    cur = con.cursor()
    cur.execute("INSERT INTO recipe_steps (recipe_id, step_no, step) VALUES (?, ?, ?)", [recipe_id, step_no, step])
    con.commit()

def insert_db(df):  
    cur = con.cursor()
    for i, row in df.iterrows():
        ingredient_list = ast.literal_eval(row["ingredients"])
        step_list = ast.literal_eval(row["steps"])

        recipe_id = insert_recipe(row)

        for ingredient_name in ingredient_list:
            ingredient_id = insert_ingredient(ingredient_name)
            insert_recipe_ingredient(recipe_id, ingredient_id)
        
        for i, step in enumerate(step_list):
            insert_recipe_step(recipe_id, i+1, step)


if __name__ == "__main__":
    init_db()
    insert_db(df)
