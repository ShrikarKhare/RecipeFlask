from re import S
from socket import create_connection
from flask import Flask, render_template, request, redirect,url_for,abort, make_response
from flask_bcrypt import Bcrypt
from wtforms import Form, StringField, PasswordField, validators
from itsdangerous import URLSafeSerializer
import sqlite3
from sqlite3 import Error
app = Flask(__name__)
bcrypt = Bcrypt(app)
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


class CreateRecipeForm(Form):
    title = StringField('Recipe Title', [validators.Length(min=4, max=50)])
    image = StringField('Image Address', [validators.Length(min=10)])
    link = StringField('Link Address', [validators.Length(min=10)])

class CreateLoginForm(Form):
    user = StringField('User', [validators.Length(min=4, max = 50)])
    password = PasswordField('Password', [validators.Length(min=4)])

class RegistrationForm(Form):
    user = StringField('User', [validators.length(min = 4, max = 50)])
    password = PasswordField('Password', [validators.length(min = 4)])

create_recipes_table = """
CREATE TABLE IF NOT EXISTS recipes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  image BLOB NOT NULL,
  link INTEGER NOT NULL
);
"""
create_user_table = '''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT NOT NULL,
    password TEXT NOT NULL
);
'''
def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

@app.route('/')
def home():
    cookie = request.cookies.get('userID')
    if cookie == None:
        return '<h1> Sorry, you are not logged in, please request access </h1>'
    fetch_query = ''' SELECT * FROM recipes'''
    allrecipes = execute_read_query(conn, fetch_query)
    return render_template("home.html", recipes=allrecipes)

@app.route('/login', methods = ['POST','GET'])
def login():
    form = CreateLoginForm()
    if request.method == "POST":
        form = CreateLoginForm(request.form)
        if form.validate():
            user = form.user.data
            password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') #bob
            user_query = "SELECT * FROM users WHERE user ='"+ user + "'"
            resp = None
            try:
                username = execute_read_query(conn, user_query)
                if username[0][1] == user and username[0][2] == password:
                    print('Logged in!')
                    resp = make_response(redirect(url_for('home')))
                    auth_s = URLSafeSerializer("secret key", "auth")
                    token = auth_s.dumps({username[0][0]})
                    data =auth_s.loads(token)
                    resp.set_cookie('userID', data)

                else:
                    raise Exception('Invalid Credentials. Please try again')
                return resp
            except Exception as e:
                print(e)
                return '<h1> Sorry, you are not logged in, please request access </h1>'
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.form)
        if form.validate():
            username = form.user.data
            password = form.password.data
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            insert_user = '''INSERT INTO users (user, password) VALUES (?,?)'''
            data = (username, hashed)
            execute_query(conn, insert_user, data)
            return redirect(url_for('login'))
    return render_template('register.html', form=form)
@app.route('/about/')
def about():
    userID = request.cookies.get('userID')
    return render_template("about.html", userID = userID)

@app.route('/recipe/delete/<id>/', methods=['POST'])
def delete_recipe(id):
    delete_query = '''DELETE FROM recipes WHERE id = ?'''
    execute_query(conn,delete_query,[id])
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

@app.route('/recipe/<id>', methods=['GET', 'POST'])
def show_recipe(id):
    form = CreateRecipeForm()
    if request.method == 'POST':
        form = CreateRecipeForm(request.form)
        if form.validate():
            title = form.title.data
            image = form.image.data
            link = form.link.data
            update_query = f'''UPDATE recipes set title=?, image=?, link=? WHERE id = {id}'''
            execute_query(conn, update_query, [title, image, link])
            return redirect(url_for('home'))
    select_query = f'''SELECT * FROM recipes WHERE id={id}'''
    recipe = execute_read_query(conn, select_query)
    form = CreateRecipeForm(link=recipe[0][3], title=recipe[0][1], image=recipe[0][2])
    return render_template('edit_recipe.html', form=form, id=id)
    
# if __name__ == '__main__':
conn = create_connection('recipes.db')

execute_query(conn,create_recipes_table)
execute_query(conn,create_user_table)

#   app.run(debug=True)