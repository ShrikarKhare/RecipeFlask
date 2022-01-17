from socket import create_connection
from flask import Flask, render_template, request, redirect,url_for,abort
from wtforms import Form, StringField, validators
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
        connection = sqlite3.connect(path, check_same_thread=False)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection
def execute_query(connection, query, values = ()):
    try:
        if len(values) > 0:
            connection.execute(query, values)
        else:
            connection.execute(query)
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
def execute_read_query(connection, query, values = ()):
    cursor = connection.cursor()
    result = None
    print(values)
    try:
        if len(values) > 0:
            cursor.execute(query)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

class CreateRecipeForm(Form):
    title = StringField('Recipe Title', [validators.Length(min=4, max=50)])
    image = StringField('Image Address', [validators.Length(min=10)])
    link = StringField('Link Address', [validators.Length(min=10)])

@app.route('/')
def home():
    
    fetch_query = ''' SELECT * FROM recipes'''
    allrecipes = execute_read_query(conn, fetch_query)
    
    return render_template("home.html", recipes=allrecipes)
    
@app.route('/about/')
def about():
    return render_template("about.html")
@app.route('/recipe/delete/<id>/', methods=['POST'])

def delete_recipe(id):
    delete_query = '''DELETE FROM recipes WHERE id = ?'''
    execute_query(conn,delete_query,id)
    return redirect(url_for('home'))

@app.route('/recipe/', methods=['POST', 'GET'])
def create_recipe():
    form = CreateRecipeForm() #instantiate the form to send when the request.method != POST
    if request.method == 'POST':
        form = CreateRecipeForm(request.form)
        if form.validate():
            title = form.title.data #access the form data
            image = form.image.data
            link = form.link.data
            insert_recipe = '''INSERT INTO recipes (title, image, link) VALUES (?,?,?)'''
            data = (title, image, link)
            execute_query(conn, insert_recipe, data)
            return redirect(url_for('home'))
    return render_template('add_recipe.html', form=form) # return the form to the template

@app.route('/recipe/<id>', methods=['POST', 'GET'])
def edit_recipe(id):
    form = CreateRecipeForm()
    if request.method == 'POST':
        form = CreateRecipeForm(request.form)
        if form.validate():
            title = form.title.data
            image = form.image.data
            link = form.link.data
            update_query = '''UPDATE recipes set title=?, image=?, link=?'''
            data = (title, image, link) 
            execute_query(conn, update_query, data)
            return redirect(url_for('home'))
    recipe = execute_read_query(
        conn, '''SELECT * FROM recipes WHERE id=?''', (id))
    
    form = CreateRecipeForm(link=recipe[0][3], title=recipe[0][1], image=recipe[0][2])
    return render_template('edit_recipe.html', form=form, id=id)
    
if __name__ == '__main__':
  conn = create_connection('recipes.db')
  
  execute_query(conn,create_recipes_table)
  app.run(debug=True)