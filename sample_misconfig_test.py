from flask import Flask

app = Flask(__name__)
# VULNERABLE: Debug mode enabled in production
# Detailed error messages can leak system info
app.config['DEBUG'] = True

@app.route("/")
def index():
    return "Hello World"
