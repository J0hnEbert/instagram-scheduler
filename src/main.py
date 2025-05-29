from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/scheduler', methods=['GET', 'POST'])
def scheduler():
    return render_template("scheduler.html")


main = app
if __name__ == "__main__":
    app.run()
    # This line is not needed in production, but useful for debugging
    
        