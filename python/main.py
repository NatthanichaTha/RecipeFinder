import pandas as pd
from fastapi import FastAPI, Response
import uvicorn
from pydantic import BaseModel, TypeAdapter
import sqlite3
import ast

con = sqlite3.connect("data/recipe.db", check_same_thread=False)


class Recipe(BaseModel):
    id: int
    name: str
    minutes: int
    calories: int | float
    nutritions: dict
    steps: list | str
    description: str
    ingredients: list

RecipeList = TypeAdapter(list[Recipe])

def get_random_recipe(minutes:int = None) -> Recipe:

    recipe = {}
    
    cur = con.cursor()
    #cur.execute("SELECT MAX(minutes) FROM recipes")
    #minutes = cur.fetchone()[0] if minutes is None else minutes
    minutes = 9999 if minutes is None else minutes 

    cur = con.cursor()
    cur.execute("SELECT * FROM recipes WHERE minutes <= ? ORDER BY RANDOM() LIMIT 1", [minutes])
    res = cur.fetchone()
    recipe["id"] = res[0]
    recipe["name"] = res[1] 
    recipe["description"] = res[2] 
    recipe["minutes"] = res[3]
    recipe["calories"] = res[4]
    recipe["nutritions"] = { "total_fat": res[5], "sugar": res[6], "sodium": res[7], "protein":res[8], "saturated_fat": res[9], "carbohydrates": res[10] }
    
    #get ingredients of the recipe 
    cur = con.cursor()
    cur.execute("SELECT ingredients.name FROM recipe_ingredients JOIN ingredients ON ingredients.id = recipe_ingredients.ingredient_id WHERE recipe_ingredients.recipe_id = ?", [recipe["id"]])
    ingredients_res = cur.fetchall()
    recipe["ingredients"] = [ingredient[0] for ingredient in ingredients_res]

    #get steps of the recipe
    cur = con.cursor()
    cur.execute("SELECT step_no, step FROM 'recipe_steps' WHERE recipe_id = ?", [recipe["id"]])
    step_res = cur.fetchall()
    recipe["steps"] = [ str(step[0]) + ". " + str(step[1]) for step in step_res]
    
    print(Recipe.model_validate(recipe))
    return Recipe.model_validate(recipe)



def get_recipe_by_ingredients(page: int, items: int, filter_ingredients: list[str], filter_n_ingredients: int = None, filter_minutes: int = None):
    filter_ingredients = set(filter_ingredients)
    offset = (page-1)*items
    
    cur = con.cursor()
    
    filter_minutes = 9999 if filter_minutes is None else filter_minutes
    filter_n_ingredients = 9999 if filter_n_ingredients is None else filter_n_ingredients

    query = f"""SELECT recipes.id, recipes.name, recipes.description, recipes.minutes, recipes.calories, recipes.total_fat, recipes.sugar, recipes.sodium, recipes.protein, recipes.saturated_fat, recipes.carbohydrates, COUNT(*)
        FROM recipes
        JOIN recipe_ingredients ON recipe_ingredients.recipe_id = recipes.id
        JOIN ingredients ON recipe_ingredients.ingredient_id = ingredients.id
        GROUP BY recipes.id, recipes.name
        HAVING COUNT(DISTINCT CASE WHEN ingredients.name IN ({", ".join(f"'{ingredient}'" for ingredient in filter_ingredients)}) THEN ingredients.name ELSE NULL END) = ? AND COUNT(*) <= ? AND minutes <= ? LIMIT {offset}, {items}"""
    
    cur.execute(query, [len(filter_ingredients) , filter_n_ingredients, filter_minutes])
    recipe_res = cur.fetchall()

    recipe_list = []

    for row in recipe_res:

        recipe = {}

        recipe["id"] = row[0]
        recipe["name"] = row[1] 
        recipe["description"] = row[2] 
        recipe["minutes"] = row[3]
        recipe["calories"] = row[4]
        recipe["nutritions"] = { "total_fat": row[5], "sugar": row[6], "sodium": row[7], "protein":row[8], "saturated_fat": row[9], "carbohydrates": row[10]}

        #get ingredients of the recipe 
        cur = con.cursor()
        cur.execute("SELECT ingredients.name FROM recipe_ingredients JOIN ingredients ON ingredients.id = recipe_ingredients.ingredient_id WHERE recipe_ingredients.recipe_id = ?", [recipe["id"]])
        ingredients_res = cur.fetchall()
        recipe["ingredients"] = [ingredient[0] for ingredient in ingredients_res]

        #get steps of the recipe
        cur = con.cursor()
        cur.execute("SELECT step_no, step FROM 'recipe_steps' WHERE recipe_id = ?", [recipe["id"]])
        step_res = cur.fetchall()
        recipe["steps"] = [ str(step[0]) + ". " + str(step[1]) for step in step_res]

        recipe_list.append(recipe)

    return recipe_list


def get_recipe_by_name(filter_name: str, page: int, items: int):

    offset = (page-1)*items
    cur = con.cursor()
    query = f"""SELECT recipes.id, recipes.name, recipes.description, recipes.minutes, recipes.calories, recipes.total_fat, recipes.sugar, recipes.sodium, recipes.protein, recipes.saturated_fat, recipes.carbohydrates FROM recipes WHERE recipes.name LIKE '%{filter_name}%' LIMIT {offset}, {items}"""

    cur.execute(query)
    recipe_res = cur.fetchall()

    recipe_list = []

    for row in recipe_res:

        recipe = {}

        recipe["id"] = row[0]
        recipe["name"] = row[1] 
        recipe["description"] = row[2] 
        recipe["minutes"] = row[3]
        recipe["calories"] = row[4]
        recipe["nutritions"] = { "total_fat": row[5], "sugar": row[6], "sodium": row[7], "protein":row[8], "saturated_fat": row[9], "carbohydrates": row[10]}

        #get ingredients of the recipe 
        cur = con.cursor()
        cur.execute("SELECT ingredients.name FROM recipe_ingredients JOIN ingredients ON ingredients.id = recipe_ingredients.ingredient_id WHERE recipe_ingredients.recipe_id = ?", [recipe["id"]])
        ingredients_res = cur.fetchall()
        recipe["ingredients"] = [ingredient[0] for ingredient in ingredients_res]

        #get steps of the recipe
        cur = con.cursor()
        cur.execute("SELECT step_no, step FROM 'recipe_steps' WHERE recipe_id = ?", [recipe["id"]])
        step_res = cur.fetchall()
        recipe["steps"] = [ str(step[0]) + ". " + str(step[1]) for step in step_res]

        recipe_list.append(recipe)

    print(recipe_list)
    return recipe_list


app = FastAPI()

@app.get("/random-recipe")
def get_random_recipe_endpoint(response: Response, minutes:int = None):
    return get_random_recipe(minutes)

@app.get("/recipe-by-ingredients")
def get_recipe_by_ingredients_endpoint(response: Response, page: int, items: int, filter_ingredients: list[str], filter_n_ingredients: int = None, filter_minutes: int = None):
    return get_recipe_by_ingredients(page, items, filter_ingredients, filter_n_ingredients, filter_minutes)

@app.get("/recipe-by-name")
def get_recipe_by_name_endpoint(filter_name: str, page: int, items: int, response: Response):
    return get_recipe_by_name(filter_name, page, items)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)