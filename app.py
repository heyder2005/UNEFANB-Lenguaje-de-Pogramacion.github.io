from flask import Flask, request, render_template

app = Flask(__name__)

USUARIOS_VALIDOS = {
    "admin": "123456",
    "goura": "goura",
    "prueba": "123",
    "manuel": "manuel",
    "kayzmel": "kayzmel",
    "edgar": "edgar",
    "heyder": "heyder"
}

@app.route('/', methods=['GET'])
def login_page():
    return render_template('peaky.html') 

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    

    if username in USUARIOS_VALIDOS and USUARIOS_VALIDOS[username] == password:

        return f"""
            <h1>¡Inicio de Sesión Exitoso! Bienvenido/a, {username}.</h1>
            <p><a href="/">Volver a iniciar sesion</a></p>
        """
    else:

        return f"""
            <h1>Error: Usuario o Contraseña Inválidos.</h1>
            <p><a href="/">Intentar de Nuevo</a></p>
        """, 401

if __name__ == '__main__':
    app.run(debug=True, port=5000)