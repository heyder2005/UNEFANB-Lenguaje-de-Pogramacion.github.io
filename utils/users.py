from werkzeug.security import generate_password_hash, check_password_hash
from .storage import load_json, save_json

USERS_KEY = "users"

def _ensure_admin():
    users = load_json(USERS_KEY, default={})
    if "admin" not in users:
        users["admin"] = {
            "password": generate_password_hash("admin"),
            "role": "coordinador",
            "meta": {"materias": {}, "disponibilidad": []}
        }
        save_json(USERS_KEY, users)
    return users

def crear_usuario(username, password, role="estudiante", meta=None):
    users = load_json(USERS_KEY, default={})
    if username in users:
        return False, "Usuario ya existe"
    users[username] = {
        "password": generate_password_hash(password),
        "role": role,
        "meta": meta or {"materias": {}, "disponibilidad": []}
    }
    save_json(USERS_KEY, users)
    return True, "Usuario creado"

def autenticar(username, password):
    users = _ensure_admin()
    u = users.get(username)
    if not u:
        return False, None
    if check_password_hash(u["password"], password):
        return True, {"username": username, "role": u.get("role"), "meta": u.get("meta", {})}
    return False, None

def obtener_usuario(username):
    users = load_json(USERS_KEY, default={})
    return users.get(username)

def guardar_usuario(username, data):
    users = load_json(USERS_KEY, default={})
    users[username] = data
    save_json(USERS_KEY, users)

def agregar_materia_docente(username, materia_id, descripcion=""):
    """
    Crea la materia para el docente si no existe.
    Devuelve (True, msg) o (False, msg).
    """
    u = obtener_usuario(username) or {}
    meta = u.setdefault("meta", {})
    materias = meta.setdefault("materias", {})
    if materia_id in materias:
        return True, "Materia ya registrada"
    materias[materia_id] = {"descripcion": descripcion}
    guardar_usuario(username, u)
    return True, "Materia agregada"

def eliminar_materia_docente(username, materia_id):
    u = obtener_usuario(username) or {}
    meta = u.get("meta", {})
    materias = meta.get("materias", {})
    if materia_id in materias:
        del materias[materia_id]
        disp = meta.get("disponibilidad", [])
        meta["disponibilidad"] = [d for d in disp if d.get("materia_id") != materia_id]
        guardar_usuario(username, u)
        return True, "Materia eliminada"
    return False, "Materia no encontrada"

def agregar_disponibilidad_range(username, materia_id, dia_idx, hora_start, hora_end):
    """
    Agrega disponibilidad en unidades de 1 franja (hora_end es índice no incluido).
    Valida solapamientos y existencia de materia.
    """
    u = obtener_usuario(username) or {}
    meta = u.setdefault("meta", {})
    materias = meta.setdefault("materias", {})
    # Si la materia no existe, crearla automáticamente
    if materia_id not in materias:
        materias[materia_id] = {"descripcion": ""}
    if hora_start >= hora_end:
        return False, "El rango de horas no es válido"
    disp = meta.setdefault("disponibilidad", [])
    # Validar solapamiento por día y materia (no permitir solaparse con otra disponibilidad del mismo docente)
    for d in disp:
        if d["dia_idx"] == int(dia_idx):
            # si los rangos se solapan
            if not (hora_end <= d["hora_start"] or hora_start >= d["hora_end"]):
                return False, "El rango se solapa con otra disponibilidad existente"
    disp.append({
        "materia_id": materia_id,
        "dia_idx": int(dia_idx),
        "hora_start": int(hora_start),
        "hora_end": int(hora_end)
    })
    guardar_usuario(username, u)
    return True, "Disponibilidad por rango agregada"

def quitar_disponibilidad_range(username, materia_id, dia_idx, hora_start, hora_end):
    u = obtener_usuario(username) or {}
    meta = u.get("meta", {})
    disp = meta.get("disponibilidad", [])
    nueva = [d for d in disp if not (
        d["materia_id"] == materia_id and d["dia_idx"] == int(dia_idx) and
        d["hora_start"] == int(hora_start) and d["hora_end"] == int(hora_end)
    )]
    if len(nueva) == len(disp):
        return False, "No se encontró esa disponibilidad exacta"
    meta["disponibilidad"] = nueva
    guardar_usuario(username, u)
    return True, "Disponibilidad eliminada"
