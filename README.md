# Parqueadero por Placas — Árbol Binario de Búsqueda

Taller de Árboles · Estructuras de Datos

Sistema de parqueadero que registra la entrada y salida de carros y motos usando un
**Árbol Binario de Búsqueda (ABB)** ordenado por placa. El código está en inglés; la
interfaz se muestra en español.

## Cómo ejecutarlo
1. Instalar dependencias:  `pip install -r requirements.txt`
2. Ejecutar:  `python app.py`
3. Abrir en el navegador:  http://127.0.0.1:5000

## Estructura
- `tree.py` → el árbol (clases `Node` y `ParkingLot`): `insert`, `search`, `delete`,
  recorridos `in_order` / `pre_order` / `post_order`, `height`, `weight`, `leaves`, `level`.
- `app.py` → servidor Flask que conecta el árbol con la página.
- `templates/index.html` → frontend en HTML (plantilla Jinja, sin JavaScript).
- `static/styles.css` → estilos.

## Operaciones del parqueadero ↔ árbol
| Parqueadero | Árbol |
|---|---|
| Registrar entrada | `insert` |
| Buscar vehículo | `search` |
| Registrar salida y cobrar | `delete` |
| Listar vehículos en orden | `in_order` |
