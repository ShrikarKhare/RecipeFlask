from socket import create_connection
from flask import Flask, render_template, request, redirect,url_for,abort
import sqlite3
from sqlite3 import Error
app = Flask(__name__)
recipes = [
        {
            "title": "BBQ Sweet and Sour Chicken Wings",
            "image": "https://image.freepik.com/free-photo/chicken-wings-barbecue-sweetly-sour-sauce-picnic-summer-menu-tasty-food-top-view-flat-lay_2829-6471.jpg",
            "link": "https://cookpad.com/us/recipes/347447-easy-sweet-sour-bbq-chicken"
        },
        {
            "title": "Hot Chicken Wings",
            "image": "https://image.freepik.com/free-photo/barbecue-chicken-wings-with-white-sesame_1339-98947.jpg",
            "link": "https://cookpad.com/us/recipes/14731185-out-of-this-world-hot-wings"
        }
    ]
def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection
def execute_query(connection, query, optional = 0):
    cursor = connection.cursor()
    # print(query)
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

create_recipes_table = """
CREATE TABLE IF NOT EXISTS recipes (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  image BLOB NOT NULL,
  link INTEGER NOT NULL
);
"""

@app.route('/')
def home():
    
    return render_template("home.html", recipes=recipes)
    
@app.route('/about/')
def about():
    return render_template("about.html")

@app.route('/recipe/', methods=['POST', 'GET'])
def create_recipe():
    form = request.form
    return redirect(url_for('home'))

if __name__ == '__main__':
  conn = create_connection('recipes.db')
  
  execute_query(conn,create_recipes_table)
  app.run(debug=True)