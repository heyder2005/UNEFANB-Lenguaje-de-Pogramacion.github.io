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

@app.route('/forgot_password', methods=['GET'])
def forgot_password():
    
    return """
        <!DOCTYPE html>
        <html lang="es">
        <head><title>Restablecer Contraseña</title>
        <style>
            body { background-color: #120536; color: white; text-align: center; font-family: Arial, sans-serif; padding-top: 50px; }
            a { color: #61f2ff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
        </head>
        <body>
            <h1>🔑 Restablecer Contraseña</h1>
            <p>Funcionalidad en desarrollo. Contacte a un administrador para asistencia.</p>
            <p><a href="/">Volver al Inicio de Sesión</a></p>
        </body>
        </html>
    """

@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register_form.html')

@app.route('/register', methods=['POST'])
def register_user():
    username = request.form.get('username')
    password = request.form.get('password')

    if username in USUARIOS_VALIDOS:
        return f"""
            <h1>Registro Fallido</h1>
            <p>El usuario <b>{username}</b> ya existe. Intenta con otro nombre.</p>
            <p><a href="/register">Intentar de Nuevo</a> | <a href="/">Ir a Login</a></p>
        """
    else:
        USUARIOS_VALIDOS[username] = password
        
        return f"""
            <h1>Registro Exitoso</h1>
            <p>El usuario <b>{username}</b> ha sido creado. ¡Ya puedes iniciar sesión!</p>
            <p><a href="/">Ir a Iniciar Sesión</a></p>
        """

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
if __name__ == '__main__':

    app.run(debug=True, port=5000)
