import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo

# mongo stores data in json like format bson
from bson.objectid import ObjectId

from werkzeug.security import generate_password_hash, check_password_hash

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
    tasks = list(mongo.db.tasks.find())
    # Along with the rendering of the template, we'll pass that tasks variable through to
    # the template: tasks=tasks. The first 'tasks' is what the template will use, and that's
    # equal to the second 'tasks',
    return render_template("tasks.html", tasks=tasks)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        
        # If there is a match in the database, and our new 'existing_user' variable is truthy, we
        # want to display a message to the user on screen, using a flash() message.
        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))
        
        # Our variable 'register' will be a dictionary, which will be inserted into the database shortly.
        # The first item in our dictionary will be "username", and that will be set to grab the username
        # value from our form, using the name="" attribute.
        # Remember, we want to store this into the database as lowercase letters.
        # Use a comma to separate each dictionary item.
        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        # If you were to include a secondary password field to confirm the user's password, you
        # would want to do that prior to building this dictionary here.
        
        # Now we can call the Users collection on MongoDB, and use the 'insert_one()' method.
        # Insert_one() requires a dictionary to be inserted, and since we've stored our dictionary inside
        # of a variable called 'register', we can just use that.
        mongo.db.users.insert_one(register)
                
        # We then want to put the newly created user into 'session', like a temporary page cookie,
        # using the session function we've imported at the top of this file.
        # The session key in square-brackets can be whatever we'd like to call it, but we'll call
        # ours "user" for now.
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))
    
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username")})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    # This new 'user' cookie will be set to the form's username supplied, in all
                    # lowercase to keep things simple, similar to how we store the username in our
                    # database.
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(request.form.get("username")))
                    return redirect(url_for("profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))
        
        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))
                                           
    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    # One way to fix this, so that users can't just force the URL to someone else's profile, is
    # to update our Profile function. If our session['user'] cookie is truthy, then we want
    # to return the appropriate profile template. However, if it's not true or doesn't exist,
    # we'll return the user back to the login template instead.
    if session["user"]:
        return render_template("profile.html", username=username)
    
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    #remove user session cookies
    # There are a couple ways to remove session cookies. First, we could just use
    # 'session.clear()', which would remove all session cookies applicable for our
    # app. Alternatively, we could use 'session.pop()', similar to JavaScript, but
    # the '.pop()' method must specify which session cookie we want to delete,
    # which is 'user' in our case. After removing the session cookie for 'user',
    # we can then redirect our user back to the login function.
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_task")
def add_task():
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_task.html", categories=categories)

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
