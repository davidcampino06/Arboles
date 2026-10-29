"""
License plate parking lot using a Binary Search Tree.
Backend: Python + Flask.  Frontend: HTML + CSS (no JavaScript).

Run:
    pip install -r requirements.txt
    python app.py
Then open in the browser: http://127.0.0.1:5000
"""
import re
from flask import Flask, render_template, request, redirect, url_for, session
from tree import ParkingLot, RATES

app = Flask(__name__)
app.secret_key = "parking-lot-bst"  # needed to show messages between page loads
parking_lot = ParkingLot()

# Colombian plates: car ABC123, motorcycle ABC12D
PLATE_PATTERNS = {"car": r"^[A-Z]{3}\d{3}$", "motorcycle": r"^[A-Z]{3}\d{2}[A-Z]$"}

# Available spots per vehicle type
CAPACITY = {"car": 12, "motorcycle": 8}

# Labels shown in the interface (Spanish)
LABELS = {"car": "Carro", "motorcycle": "Moto"}


def clean_plate(plate):
    return plate.strip().upper().replace("-", "").replace(" ", "")


def notify(text, kind="ok"):
    """Stores a message to show it on the next page load."""
    session["message"] = {"text": text, "kind": kind}


def format_money(value):
    return "$" + f"{value:,}".replace(",", ".")


def count_vehicles(vehicle_type):
    return sum(1 for n in parking_lot.in_order(parking_lot.root, [])
               if n.vehicle_type == vehicle_type)


@app.route("/")
def index():
    root = parking_lot.root
    vehicles = [
        {"plate": n.plate, "vehicle_type": n.vehicle_type,
         "entry_time": n.entry_time.strftime("%H:%M:%S"),
         "level": parking_lot.level(n.plate)}
        for n in parking_lot.in_order(root, [])
    ]
    tree_data = {
        "root": root.plate if root else "—",
        "height": parking_lot.height(root),
        "weight": parking_lot.weight(root),
        "leaves": parking_lot.leaves(root, []),
        "in_order": [n.plate for n in parking_lot.in_order(root, [])],
        "pre_order": [n.plate for n in parking_lot.pre_order(root, [])],
        "post_order": [n.plate for n in parking_lot.post_order(root, [])],
    }
    spots = {}
    for vehicle_type, total in CAPACITY.items():
        parked = [v for v in vehicles if v["vehicle_type"] == vehicle_type]
        spots[vehicle_type] = {
            "occupied": len(parked), "total": total, "free": total - len(parked),
            "percentage": round(len(parked) * 100 / total), "vehicles": parked,
        }
    return render_template(
        "index.html",
        spots=spots,
        tree=tree_data,
        vehicles=vehicles,
        drawing=parking_lot.layout(),
        labels=LABELS,
        message=session.pop("message", None),
        ticket=session.pop("ticket", None),
        searched=session.pop("searched", None),
        rates={k: format_money(v) for k, v in RATES.items()},
    )


@app.route("/entry", methods=["POST"])
def entry():
    plate = clean_plate(request.form.get("plate", ""))
    vehicle_type = request.form.get("vehicle_type", "car")

    if vehicle_type not in PLATE_PATTERNS:
        notify("Tipo de vehículo no válido.", "error")
    elif not re.match(PLATE_PATTERNS[vehicle_type], plate):
        example = "ABC123" if vehicle_type == "car" else "ABC12D"
        notify(f"Placa inválida para {LABELS[vehicle_type]}. Ejemplo: {example}", "error")
    elif count_vehicles(vehicle_type) >= CAPACITY[vehicle_type]:
        notify(f"No hay cupos disponibles para {LABELS[vehicle_type].lower()}s.", "error")
    elif not parking_lot.insert(plate, vehicle_type):
        notify(f"El vehículo {plate} ya está en el parqueadero.", "error")
    else:
        notify(f"Entrada registrada: {plate} ({LABELS[vehicle_type]}).")
    return redirect(url_for("index"))


@app.route("/search", methods=["POST"])
def search():
    plate = clean_plate(request.form.get("plate", ""))
    action = request.form.get("action", "search")
    node = parking_lot.search(plate)

    if node is None:
        notify(f"{plate or 'La placa'} no está en el parqueadero.", "error")
        return redirect(url_for("index"))

    minutes, fee = parking_lot.calculate_fee(node)
    level = parking_lot.level(plate)

    if action == "exit":
        parking_lot.delete(plate)
        notify(f"Salida de {plate}: {minutes} min. Total a pagar {format_money(fee)}.")
    else:
        session["searched"] = plate
        session["ticket"] = {
            "plate": node.plate, "vehicle_type": node.vehicle_type,
            "entry_time": node.entry_time.strftime("%H:%M:%S"),
            "level": level, "minutes": minutes, "fee": format_money(fee),
        }
        notify(f"{plate} encontrado en el nivel {level} del árbol.")
    return redirect(url_for("index"))


@app.route("/demo", methods=["POST"])
def demo():
    """Loads sample vehicles for the presentation."""
    for plate, vehicle_type in [("MNO456", "car"), ("FGH789", "car"), ("TUV321", "car"),
                                ("CDE45A", "motorcycle"), ("JKL234", "car"),
                                ("RST67B", "motorcycle"), ("XYZ890", "car")]:
        parking_lot.insert(plate, vehicle_type)
    notify("Vehículos de ejemplo cargados.")
    return redirect(url_for("index"))


@app.route("/clear", methods=["POST"])
def clear():
    parking_lot.root = None
    notify("Parqueadero vaciado.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
