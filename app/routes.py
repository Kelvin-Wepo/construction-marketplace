from flask import render_template
from app import app

@app.route('/documentation')
def documentation():
    return render_template('documentation.html')
