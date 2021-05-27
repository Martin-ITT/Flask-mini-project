import os
from flask import (
    Flask, flash, render_template, 
    redirect, request, url_for)
from flask_pymongo import PyMongo

# mongo stores data in json like format bson
from bson.objectid import ObjectId

# once deployed on heroku app.py won't be able to find env.py
if os.path.exists("env.py"):
    import env


# create an instance of Flask and store in variable app
app = Flask(__name__)

# grab DB name
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
# config connection string
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
# grab secret key
app.secret_key = os.environ.get("SECRET_KEY")

# setup an instance of pymongo
mongo = PyMongo(app)

# Remember the routing is a string that, when we attach it to a URL, will redirect to a
# particular function in our Flask app.
# I'm going to add it directly beneath our existing default root here, so that either
# URL will direct the user to the same page.
@app.route("/")
@app.route("/get_tasks")
# test function hello
def get_tasks():
    # On this tasks template, we want to be able to generate data from our tasks collection
    # on MongoDB, visible to our users. This will find all documents from the tasks collection,
    # and assign them to our new 'tasks' variable.
    tasks = mongo.db.tasks.find()
    # Along with the rendering of the template, we'll pass that tasks variable through to
    # the template: tasks=tasks. The first 'tasks' is what the template will use, and that's
    # equal to the second 'tasks',
    return render_template("tasks.html", tasks=tasks)


"""
The final step to test our application, is to tell our app how and where to run our application.
This is the same process we've seen before, but this time we've set our IP and PORT environment
variables in the hidden env.py file.
The host will be set to the IP, so we need to type os.environ.get("IP") in order to fetch
that default value, which was "0.0.0.0".
The port will need to be converted to an integer, so we'll type: int(os.environ.get("PORT")).
Don't forget to separate each parameter with a comma.
Our final parameter will be debug=True, because during development, we want to see the actual
errors that may appear, instead of a generic server warning.
Make sure to update this to debug=False prior to actual deployment or project submission.
"""
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
