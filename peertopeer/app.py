<<<<<<< HEAD
from flask import Flask, render_template,uest, redirect, url_for, flash
=======
from flask import Flask, render_template #,uest, redirect, url_for, flash
from db.admin import Admin
>>>>>>> DB/main

app = Flask(__name__)

@app.route('/')
def home():
<<<<<<< HEAD
=======
    a=Admin()
    # a.logInAlumn('22301061553360','22301061553360@cetis155.edu.mx','7839123848','contraseñ','pepito',3,'A')
    # a.logInTutor('22301061553361','22301061553361@cetis155.edu.mx','7839120048','contraseñ','oscar','guzaman alvedo','1234123340989301','josefa ortiz de dominguez','bachillerato')
    a.close()
    
>>>>>>> DB/main
    return render_template("principal.html")

if __name__ == "__main__":
    app.run(debug=True)