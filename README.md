# Parqueadero por Placas — Árbol Binario de Búsqueda

Taller de Árboles · Estructuras de Datos

## Cómo ejecutarlo
1. Instalar dependencias:  `pip install -r requirements.txt`
2. Entrar a la carpeta del proyecto y ejecutar:  `python app.py`
3. Abrir en el navegador:  http://127.0.0.1:5000

## Estructura
- `arbol.py` → el Árbol Binario de Búsqueda (clases `Nodo` y `Parqueadero`): insertar, buscar,
  eliminar, recorridos (in/pre/post-order), altura, peso, hojas, nivel.
- `app.py` → servidor Flask que conecta el árbol con la página.
- `templates/index.html` → frontend en HTML (plantilla Jinja, sin JavaScript).
- `static/styles.css` → estilos.

## Operaciones del parqueadero ↔ árbol
| Parqueadero | Árbol |
|---|---|
| Registrar entrada | Insertar nodo |
| Buscar vehículo | Buscar por placa |
| Registrar salida y cobrar | Eliminar nodo |
| Listar vehículos en orden | Recorrido in-order |
