from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import requests
from requests.structures import CaseInsensitiveDict
from key_generator.key_generator import generate
import json
import time
import atexit

from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__, template_folder='/Users/zacharygoldstein/PycharmProjects/VCC7.0/pythonlogin/templates')

# Change this to your secret key (can be anything, it's for extra protection)

# generated_key = secrets.token_urlsafe(16)

app.secret_key = '12345'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pythonlogin'

# Intialize MySQL
mysql = MySQL(app)

key1 = generate(seed=101)
generated_key = key1.get_key()


def callapi():
    # there is inbuilt json() constructor for requests.get() method
    json_data = requests.get("http://3.70.154.20:3500/eth/v1alpha1/beacon/chainhead").json()
    # print(json.dumps(json_data, indent=4))

    # To actually write the data to the file, we just call the dump() function from json library
    with open('personal.json', 'w') as json_file:
        json.dump(json_data, json_file)

    return json.dumps(json_data, indent=4);

scheduler = BackgroundScheduler()
scheduler.add_job(func=callapi, trigger="interval", seconds=60)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


@app.route('/')
def hello_world():
    return 'Go to the /login page'


# http://localhost:5000/login/ - the following will be our login page, which will use both GET and POST requests
@app.route('/login/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page

            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)


# http://localhost:5000/login/logout - this will be the logout page
@app.route('/login/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/login/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/login/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


# http://localhost:5000/login/home - this will be the home page, only accessible for loggedin users
@app.route('/login/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'], id=session['id'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/login/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/login/key')
def getapikey():
    if 'loggedin' in session:
        # generated_key = 'XXXX-XXXX-XXXX-XXXX-XXXX'

        return render_template('key.html', username=session['username'], generated_key=generated_key);


@app.route('/login/key/keyapi')
def postapiheaders():
    if 'loggedin' in session:
        # s = Selenium2Library.Selenium2Library()
        # url = s.get_location()
        query_string = request.query_string

        query_string = query_string.decode()

        # code = query_string.split('fapi?')[0]

        # print(query_string)

        if generated_key in query_string:

            # beaconurl = "http://3.70.154.20:3500/eth/v1alpha1/beacon/chainhead"

            with open('/Users/zacharygoldstein/PycharmProjects/VCC7.0/personal.json', 'r') as f:
                data = json.load(f)


            # headers = CaseInsensitiveDict()
            # headers["Accept"] = "application/json"

            # resp = requests.get(beaconurl, headers=headers)

            return render_template('keyapi.html', username=session['username'], response=callapi());
        else:
            return render_template('keyapi.html', username=session['username'],
                                   response='Wrong API Key, please try again!');
