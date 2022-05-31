# VCC


## Installation

Install with pip:

```
$ pip install -r requirements.txt
```

## Run Flask
### Run flask for develop

```
$ pip install -U flask
$ export FLASK_APP=path/too/main.py
$ flask run
```
In flask, Default port is `5000`

## Setting up the SQL DB

Open up/download MySQL Workbech, and put in these credentials

```
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pythonlogin'
```
 
## Navigating the App

This app is a simple gui, register -> login -> go to home -> get api key -> enter in api key -> see the fun eth data!!!
