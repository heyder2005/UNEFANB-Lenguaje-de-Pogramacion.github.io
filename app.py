from flask import Flask, render_template, request, redirect, url_for, session, flash
from utils.users import (
    autenticar, crear_usuario, obtener_usuario,
    agregar_materia_docente, eliminar_materia_docente,
    agregar_disponibilidad_range, quitar_disponibilidad_range
)
from utils.horario import (
    DIAS,
    HORAS_STARTS,
    HORAS_LABELS,
    cargar_matriz,
    guardar_matriz,
    obtener_ofertas_desde_matriz
)
from utils.storage import load_json, save_json

app = Flask(__name__)
app.secret_key = "cambia_esta_clave_local_y_segura"  


@app.route("/", methods=["GET"])
def inicio():
    return render_template("peaky.html")


@app.route("/forgot_password", methods=["GET"])
def forgot_password():
    return render_template("forgot_password.html")


@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "estudiante")
        if not username or not password:
            flash("Usuario y contraseña son obligatorios")
            return redirect(url_for("register_page"))
        ok, msg = crear_usuario(username, password, role)
        flash(msg)
        if ok:
            return redirect(url_for("inicio"))
        return redirect(url_for("register_page"))
    return render_template("register_form.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    ok, info = autenticar(username, password)
    if ok:
        session["user"] = info["username"]
        session["role"] = info["role"]
        if info["role"] == "docente":
            return redirect(url_for("docente"))
        if info["role"] == "coordinador":
            return redirect(url_for("coordinador"))
        return redirect(url_for("estudiante"))
    flash("Usuario o contraseña inválidos")
    return redirect(url_for("inicio"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("inicio"))


def login_required(role=None):
    from functools import wraps

    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not session.get("user"):
                flash("Inicia sesión primero")
                return redirect(url_for("inicio"))
            if role and session.get("role") != role:
                flash("No tienes permiso para acceder a esta página")
                return redirect(url_for("inicio"))
            return f(*args, **kwargs)

        return wrapped

    return decorator


@app.route("/docente", methods=["GET", "POST"])
@login_required(role="docente")
def docente():
    user = session["user"]
    u = obtener_usuario(user) or {}
    materias = u.get("meta", {}).get("materias", {})
    disponibilidad = u.get("meta", {}).get("disponibilidad", [])

    if request.method == "POST":
        action = request.form.get("action")
        if action == "add_materia":
            mid = request.form.get("materia_id", "").strip()
            desc = request.form.get("descripcion", "").strip()
            if not mid:
                flash("Id de materia obligatorio")
                return redirect(url_for("docente"))
            ok, msg = agregar_materia_docente(user, mid, desc)
            flash(msg)
            return redirect(url_for("docente"))

        if action == "remove_materia":
            mid = request.form.get("materia_id", "").strip()
            ok, msg = eliminar_materia_docente(user, mid)
            flash(msg)
            return redirect(url_for("docente"))

        if action == "add_disponibilidad_range":
            
            mid_sel = request.form.get("materia_id_sel", "").strip()
            if not mid_sel:
                flash("Debes seleccionar una materia registrada.")
                return redirect(url_for("docente"))

            try:
                dia_idx = int(request.form.get("dia_idx"))
                hora_start = int(request.form.get("hora_start"))
                hora_end = int(request.form.get("hora_end"))
            except Exception:
                flash("Datos de horario inválidos")
                return redirect(url_for("docente"))

            if hora_end <= hora_start:
                flash("El rango debe tener al menos una franja.")
                return redirect(url_for("docente"))

            ok, msg = agregar_disponibilidad_range(user, mid_sel, dia_idx, hora_start, hora_end)
            flash(msg)
            return redirect(url_for("docente"))

        if action == "remove_disponibilidad_range":
            mid = request.form.get("materia_id_sel", "").strip()
            try:
                dia_idx = int(request.form.get("dia_idx"))
                hora_start = int(request.form.get("hora_start"))
                hora_end = int(request.form.get("hora_end"))
            except Exception:
                flash("Datos inválidos para eliminar disponibilidad")
                return redirect(url_for("docente"))
            ok, msg = quitar_disponibilidad_range(user, mid, dia_idx, hora_start, hora_end)
            flash(msg)
            return redirect(url_for("docente"))

    return render_template(
        "docente.html",
        user=user,
        materias=materias,
        disponibilidad=disponibilidad,
        DIAS=DIAS,
        HORAS_STARTS=HORAS_STARTS,
        HORAS_LABELS=HORAS_LABELS,
    )


def load_users_for_coordinator():
    users = load_json("users", default={})
    docentes = {}
    for uname, u in users.items():
        if u.get("role") == "docente":
            docentes[uname] = u.get("meta", {}).get("materias", {})
    return docentes


@app.route("/coordinador", methods=["GET", "POST"])
@login_required(role="coordinador")
def coordinador():
    matriz = cargar_matriz()
    if request.method == "POST":
        action = request.form.get("action")
        if action == "asignar":
            docente_id = request.form.get("docente_id").strip()
            materia_id = request.form.get("materia_id").strip()
            try:
                dia_idx = int(request.form.get("dia_idx"))
                hora_start = int(request.form.get("hora_start"))
                hora_end = int(request.form.get("hora_end"))
            except Exception:
                flash("Datos de asignación inválidos")
                return redirect(url_for("coordinador"))

            docente = obtener_usuario(docente_id)
            if not docente:
                flash("Docente no encontrado")
                return redirect(url_for("coordinador"))

            materias_doc = docente.get("meta", {}).get("materias", {})
            disp_doc = docente.get("meta", {}).get("disponibilidad", [])

            if materia_id not in materias_doc:
                flash("El docente no declaró esa materia")
                return redirect(url_for("coordinador"))

            if hora_start >= hora_end:
                flash("Rango de horas inválido")
                return redirect(url_for("coordinador"))

            for h in range(hora_start, hora_end):
                if h >= len(HORAS_STARTS):
                    flash("Rango fuera de horario")
                    return redirect(url_for("coordinador"))
                found = False
                for d in disp_doc:
                    if d["dia_idx"] == dia_idx and d["materia_id"] == materia_id:
                        if d["hora_start"] <= h < d["hora_end"]:
                            found = True
                            break
                if not found:
                    flash(f"Docente no disponible en {DIAS[dia_idx]} {HORAS_LABELS[h]}")
                    return redirect(url_for("coordinador"))

            for h in range(hora_start, hora_end):
                if matriz[dia_idx][h] is not None:
                    flash("Choque con otra asignación")
                    return redirect(url_for("coordinador"))

            for h in range(hora_start, hora_end):
                matriz[dia_idx][h] = {"materia_id": materia_id, "docente_id": docente_id, "estudiantes": []}
            guardar_matriz(matriz)
            flash("Asignación realizada")
            return redirect(url_for("coordinador"))

        if action == "retirar":
            try:
                dia_idx = int(request.form.get("dia_idx"))
                hora_idx = int(request.form.get("hora_idx"))
            except Exception:
                flash("Datos inválidos para retirar")
                return redirect(url_for("coordinador"))
            if matriz[dia_idx][hora_idx] is None:
                flash("No hay asignación en esa celda")
            else:
                matriz[dia_idx][hora_idx] = None
                guardar_matriz(matriz)
                flash("Asignación retirada")
            return redirect(url_for("coordinador"))

    docentes = load_users_for_coordinator()
    return render_template(
        "coordinador.html",
        matriz=matriz,
        DIAS=DIAS,
        HORAS_STARTS=HORAS_STARTS,
        HORAS_LABELS=HORAS_LABELS,
        docentes=docentes,
    )


@app.route("/estudiante", methods=["GET", "POST"])
@login_required(role="estudiante")
def estudiante():
    matriz = cargar_matriz()
    ofertas = obtener_ofertas_desde_matriz(matriz)

    if request.method == "POST":
        action = request.form.get("action")
        user = session["user"]

        if action == "inscribir_oferta":
            oferta_id = request.form.get("oferta_id")
            if not oferta_id:
                flash("Oferta inválida")
                return redirect(url_for("estudiante"))
            try:
                parts = oferta_id.split("_")
                dia_idx = int(parts[0][1:])
                hora_start = int(parts[1][1:])
                hora_end = int(parts[2][1:])
            except Exception:
                flash("Oferta inválida")
                return redirect(url_for("estudiante"))

            celda = matriz[dia_idx][hora_start]
            if not celda:
                flash("La oferta ya no está disponible")
                return redirect(url_for("estudiante"))
            materia = celda.get("materia_id")
            docente = celda.get("docente_id")
            for h in range(hora_start, hora_end):
                c = matriz[dia_idx][h]
                if not c or c.get("materia_id") != materia or c.get("docente_id") != docente:
                    flash("La oferta ya no está disponible")
                    return redirect(url_for("estudiante"))
            already = False
            for h in range(hora_start, hora_end):
                inscritos = matriz[dia_idx][h].setdefault("estudiantes", [])
                if user in inscritos:
                    already = True
                else:
                    inscritos.append(user)
            guardar_matriz(matriz)

            
            start_label = HORAS_LABELS[hora_start].split(" - ")[0]
            end_label = HORAS_LABELS[hora_end - 1].split(" - ")[1]
            if already:
                flash("Ya estabas inscrito en parte o toda la oferta; se actualizó la inscripción")
            else:
                flash(f"Inscripción realizada en {materia} ({DIAS[dia_idx]} {start_label} - {end_label})")
            return redirect(url_for("estudiante"))

        if action == "solicitar_materia":
            materia_id = request.form.get("materia_id", "").strip()
            if not materia_id:
                flash("Escribe el id de la materia")
                return redirect(url_for("estudiante"))
            solicitudes = load_json("solicitudes", default=[])
            solicitudes.append({"user": user, "materia_id": materia_id})
            save_json("solicitudes", solicitudes)
            flash("Solicitud enviada al coordinador")
            return redirect(url_for("estudiante"))

    return render_template(
        "estudiante.html",
        matriz=matriz,
        DIAS=DIAS,
        HORAS_STARTS=HORAS_STARTS,
        HORAS_LABELS=HORAS_LABELS,
        ofertas=ofertas,
    )


@app.route("/imprimir")
@login_required()
def imprimir():
    matriz = cargar_matriz()
    return render_template(
        "imprimir.html",
        user=session.get("user"),
        role=session.get("role"),
        matriz=matriz,
        DIAS=DIAS,
        HORAS_STARTS=HORAS_STARTS,
        HORAS_LABELS=HORAS_LABELS,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
