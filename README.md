# RecipeFinder
A FastAPI-based backend that provides endpoints for fetching and filtering recipes from a database with over 200k+ recipes! It allows users to retrieve random recipes, search recipes by ingredients, and search recipes by name.

![RecipeFinder Logo](logo.png)

## Features
- **Get Random Recipe:** Retrieve a random recipe with an optional filter for maximum preparation time.
- **Get Recipes by Ingredients:** Search for recipes based on a list of ingredients, with optional filters for the number of ingredients and maximum preparation time.
- **Get Recipes by Name:** Search for recipes based on a partial match of the recipe name, with pagination support.

## Installation
### Prerequisites
- Python 3.8+
- pip (Python package installer)

## Steps
1. Clone the repository:

    ` git clone git@github.com:NatthanichaTha/RecipeFinder.git
    cd RecipeFinder
    `

2. Create and activate a Conda environment:

    ``conda create --name recipefinder python=3.10
    conda activate recipefinder
    ``

3. Install the required dependencies:

    `pip install -r requirements.txt
    `

4. Prepare the SQLite database:
- Ensure your `RAW_recipes.csv` file is placed in the `script` directory.
- Run the script to generate the SQLite database:

    `python script/generate_sqlite_from_csv.py
    `

5. Start the FastAPI application:

    `uvicorn main:app --reload
    `

## Usage
### Endpoints

- GET /random-recipe
    - Description: Fetch a random recipe.
    - Query Parameters:
        - `minutes` (optional): Limit the maximum preparation time.
    - Example:

        `` curl -X 'GET' 'http://127.0.0.1:8000/random-recipe?minutes=30' -H 'accept: application/json' ``

- GET /recipe-by-ingredients

    - Description: Fetch recipes by a list of ingredients. Supports pagination and optional filters for the number of ingredients and preparation time.
   - Query Parameters:
        - `page`: The page number for pagination.
        - `items`: The number of items per page.
        - `filter_ingredients`: A list of ingredients to filter by.
        - `filter_n_ingredients` (optional): Maximum number of ingredients in the recipe.
        filter_minutes (optional): Maximum preparation time.
    - Example:

        ``
        curl -X 'GET' 'http://127.0.0.1:8000/recipe-by-ingredients?page=1&items=5' --header 'Content-Type: application/json'  -d '["egg", "milk"]'
        ``

- GET /recipe-by-name
    - Description: Fetch recipes by name with support for pagination.
    - Query Parameters: 
        - filter_name: The name to filter by (partial match).
        - page: The page number for pagination.
        - items: The number of items per page.
    - Example:

        `` curl -X 'GET' 'http://127.0.0.1:8000/recipe-by-name?filter_name=pancake&page=1&items=5' -H 'accept: application/json' ``

## Project Structure
- `main.py`: Main application file with FastAPI endpoints.
- `script/generate_sqlite_from_csv.py`: Script to generate SQLite database from CSV file.
- `data/recipe.db`: SQLite database file (generated by the script).

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any improvements. 🙏








