import os
from flask import Flask
# once deployed on heroku app.py won't be able to find env.py
if os.path.exists("env.py"):
    import env


#create an instance of Flask and store in variable app
app = Flask(__name__)

@app.route("/")
#test function hello
def hello():
    return "Hello world ... again!"


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