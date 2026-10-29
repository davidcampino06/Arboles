"""
Parqueadero por placas con Árbol Binario de Búsqueda.
Backend: Python + Flask.  Frontend: HTML + CSS (sin JavaScript).

Ejecutar:
    pip install flask
    python app.py
Luego abrir en el navegador: http://127.0.0.1:5000
"""
import re
from flask import Flask, render_template, request, redirect, url_for, session
from arbol import Parqueadero, TARIFAS

app = Flask(__name__)
app.secret_key = "parqueadero-abb"  # necesario para mostrar mensajes entre páginas
parqueadero = Parqueadero()

# Placas colombianas: carro ABC123, moto ABC12D
PATRONES = {"Carro": r"^[A-Z]{3}\d{3}$", "Moto": r"^[A-Z]{3}\d{2}[A-Z]$"}

# Cupos disponibles por tipo de vehículo
CAPACIDAD = {"Carro": 12, "Moto": 8}


def limpiar(placa):
    return placa.strip().upper().replace("-", "").replace(" ", "")


def avisar(texto, tipo="ok"):
    """Guarda un mensaje para mostrarlo en la siguiente carga de la página."""
    session["mensaje"] = {"texto": texto, "tipo": tipo}


def pesos(valor):
    return "$" + f"{valor:,}".replace(",", ".")


@app.route("/")
def inicio():
    raiz = parqueadero.root
    vehiculos = [
        {"placa": n.placa, "tipo": n.tipo,
         "entrada": n.hora_entrada.strftime("%H:%M:%S"),
         "nivel": parqueadero.nivel(n.placa)}
        for n in parqueadero.in_order(raiz, [])
    ]
    datos = {
        "raiz": raiz.placa if raiz else "—",
        "altura": parqueadero.altura(raiz),
        "peso": parqueadero.peso(raiz),
        "hojas": parqueadero.hojas(raiz, []),
        "in_order": [n.placa for n in parqueadero.in_order(raiz, [])],
        "pre_order": [n.placa for n in parqueadero.pre_order(raiz, [])],
        "post_order": [n.placa for n in parqueadero.post_order(raiz, [])],
    }
    ocupados = {t: sum(1 for v in vehiculos if v["tipo"] == t) for t in CAPACIDAD}
    cupos = {t: {"ocupados": ocupados[t], "total": CAPACIDAD[t],
                 "libres": CAPACIDAD[t] - ocupados[t],
                 "porcentaje": round(ocupados[t] * 100 / CAPACIDAD[t]),
                 "lista": [v for v in vehiculos if v["tipo"] == t]}
             for t in CAPACIDAD}
    return render_template(
        "index.html",
        cupos=cupos,
        datos=datos,
        vehiculos=vehiculos,
        dibujo=parqueadero.posiciones(),
        mensaje=session.pop("mensaje", None),
        resultado=session.pop("resultado", None),
        buscado=session.pop("buscado", None),
        tarifas={k: pesos(v) for k, v in TARIFAS.items()},
    )


@app.route("/entrada", methods=["POST"])
def entrada():
    placa = limpiar(request.form.get("placa", ""))
    tipo = request.form.get("tipo", "Carro")

    if tipo not in PATRONES:
        avisar("Tipo de vehículo no válido.", "error")
    elif not re.match(PATRONES[tipo], placa):
        ejemplo = "ABC123" if tipo == "Carro" else "ABC12D"
        avisar(f"Placa inválida para {tipo}. Ejemplo: {ejemplo}", "error")
    elif sum(1 for n in parqueadero.in_order(parqueadero.root, []) if n.tipo == tipo) >= CAPACIDAD[tipo]:
        avisar(f"No hay cupos disponibles para {tipo.lower()}s.", "error")
    elif not parqueadero.insertar(placa, tipo):
        avisar(f"El vehículo {placa} ya está en el parqueadero.", "error")
    else:
        avisar(f"Entrada registrada: {placa} ({tipo}).")
    return redirect(url_for("inicio"))


@app.route("/buscar", methods=["POST"])
def buscar():
    placa = limpiar(request.form.get("placa", ""))
    accion = request.form.get("accion", "buscar")
    nodo = parqueadero.buscar(placa)

    if nodo is None:
        avisar(f"{placa or 'La placa'} no está en el parqueadero.", "error")
        return redirect(url_for("inicio"))

    minutos, cobro = parqueadero.calcular_cobro(nodo)

    if accion == "salida":
        parqueadero.eliminar(placa)
        avisar(f"Salida de {placa}: {minutos} min. Total a pagar {pesos(cobro)}.")
    else:
        session["buscado"] = placa
        session["resultado"] = {
            "placa": nodo.placa, "tipo": nodo.tipo,
            "entrada": nodo.hora_entrada.strftime("%H:%M:%S"),
            "nivel": parqueadero.nivel(placa),
            "minutos": minutos, "cobro": pesos(cobro),
        }
        avisar(f"{placa} encontrado en el nivel {parqueadero.nivel(placa)} del árbol.")
    return redirect(url_for("inicio"))


@app.route("/demo", methods=["POST"])
def demo():
    """Carga vehículos de ejemplo para la presentación."""
    for placa, tipo in [("MNO456", "Carro"), ("FGH789", "Carro"), ("TUV321", "Carro"),
                        ("CDE45A", "Moto"), ("JKL234", "Carro"), ("RST67B", "Moto"),
                        ("XYZ890", "Carro")]:
        parqueadero.insertar(placa, tipo)
    avisar("Vehículos de ejemplo cargados.")
    return redirect(url_for("inicio"))


@app.route("/vaciar", methods=["POST"])
def vaciar():
    parqueadero.root = None
    avisar("Parqueadero vaciado.")
    return redirect(url_for("inicio"))


if __name__ == "__main__":
    app.run(debug=True)
