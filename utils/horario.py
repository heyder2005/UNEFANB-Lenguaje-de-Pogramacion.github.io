from datetime import datetime, timedelta
from .storage import load_json, save_json

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]

def generar_franjas_45(start="07:00", end="16:00"):
    fmt = "%H:%M"
    inicio = datetime.strptime(start, fmt)
    fin = datetime.strptime(end, fmt)
    delta = timedelta(minutes=45)
    t = inicio
    starts = []
    labels = []
    while t < fin:
        start_str = t.strftime(fmt)
        next_t = t + delta
        end_str = next_t.strftime(fmt)
        starts.append(start_str)
        labels.append(f"{start_str} - {end_str}")
        t = next_t
    return starts, labels

# Genera las franjas y etiquetas (ej: "07:00 - 07:45", "07:45 - 08:30", ...)
HORAS_STARTS, HORAS_LABELS = generar_franjas_45("07:00", "16:00")

def crear_matriz_vacia():
    return [[None for _ in HORAS_STARTS] for _ in DIAS]

def cargar_matriz():
    m = load_json("matriz", default=None)
    if m is None or not m:
        m = crear_matriz_vacia()
        save_json("matriz", m)
    return m

def guardar_matriz(m):
    save_json("matriz", m)

def _add_minutes_to_time(hora_str, minutes):
    fmt = "%H:%M"
    t = datetime.strptime(hora_str, fmt)
    t += timedelta(minutes=minutes)
    return t.strftime(fmt)

def obtener_ofertas_desde_matriz(matriz):
    """
    Recorre la matriz y agrupa celdas contiguas de la misma materia/docente
    en una sola oferta. La etiqueta hora_label ahora usa la hora de inicio
    de la primera franja y la hora de fin (fin de la última franja) del bloque.
    """
    ofertas = []
    for dia_idx, fila in enumerate(matriz):
        col = 0
        while col < len(fila):
            celda = fila[col]
            if not celda:
                col += 1
                continue
            materia = celda.get("materia_id")
            docente = celda.get("docente_id")
            start = col
            end = start + 1
            while end < len(fila):
                next_celda = fila[end]
                if not next_celda:
                    break
                if next_celda.get("materia_id") == materia and next_celda.get("docente_id") == docente:
                    end += 1
                else:
                    break
            # hora de inicio = inicio de la franja 'start'
            hora_inicio = HORAS_STARTS[start]
            # hora de fin = fin de la franja 'end-1' (sumar 45 minutos a su inicio)
            ultima_fr_inicio = HORAS_STARTS[end - 1]
            hora_fin = _add_minutes_to_time(ultima_fr_inicio, 45)
            hora_label = f"{hora_inicio} - {hora_fin}"
            ofertas.append({
                "id": f"d{dia_idx}_s{start}_e{end}",
                "materia_id": materia,
                "docente_id": docente,
                "dia_idx": dia_idx,
                "hora_start": start,
                "hora_end": end,
                "hora_label": hora_label
            })
            col = end
    ofertas.sort(key=lambda x: (x["dia_idx"], x["hora_start"]))
    return ofertas
