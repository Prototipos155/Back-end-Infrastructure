from flask import Flask, render_template, request, redirect, url_for, flash

import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("home.html")

@app.route ('/iniciarSesion')
def iniciarSesion():
    return render_template("iniciosesi.html")

@app.route ('/registro')
def registro():
    return render_template("registro.html")

if __name__ == "__main__":
    app.run(debug=True)