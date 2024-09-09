from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("principal.html")

@app.route ('/iniciarSesion')
def iniciarSesion():
    return render_template("iniciosesi.html")

@app.route ('/registro')
def registro():
    return render_template("registro.html")

if __name__ == "__main__":
    app.run(debug=True)