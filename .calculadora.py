from flask import Flask, request
app = app = Flask(__name__)

@app.route('/')
def calculator():
    return """
    <style>#k{color:grey;} #k1{color:#1a2421;background-color:#cbcbcb;}</style>
    <form method="POST" action="/calculate">
	<label id="k">Ingresa primer número:</label>
	<input type="number" id="k1" name="n1"><br><br>
	<label id="k">Ingresa segundo número:</label>
	<input type="number" id="k1" name="n2"><br><br>
	<label>Selecciona un operador:</label>
	<select name="opr" id="op">
		<option value="add">+</option>
		<option value="sub">-</option>
		<option value="mul">*</option>
		<option value="div">/</option>
	</select><br><br>
	<input type="submit">
</form>"""
@app.route("/calculate", methods=["POST"])
def calculate():
    n1 = int(request.form['n1'])
    n2 = int(request.form['n2'])
    oper = str(request.form['opr'])
    r=0
    if oper =="add":
        r = n1 + n2
    elif oper =="sub":
        r = n1 - n2
    elif oper == "mul":
        r = n1 * n2
    elif oper == "div":
        if n2 == 0:
            r = "Error, división por cero"
        else:
            r = n1 /n2
        
    return f"""
    <h1>Resultado: {r}</h1>
    <a href="/">Volver a la calculadora</a>"""
if __name__ == '__main__':
    app.run(debug=True,port=7770)

