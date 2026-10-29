"""
Árbol Binario de Búsqueda (ABB) para un parqueadero.
Cada nodo es un vehículo y el árbol se ordena por PLACA (orden alfabético).
"""
from datetime import datetime
import math

# Tarifas por hora o fracción
TARIFAS = {"Carro": 4000, "Moto": 2000}


class Nodo:
    def __init__(self, placa, tipo):
        self.placa = placa
        self.tipo = tipo
        self.hora_entrada = datetime.now()
        self.left = None
        self.right = None


class Parqueadero:
    def __init__(self):
        self.root = None

    # ---------- INSERTAR (entrada de vehículo) ----------
    def insertar(self, placa, tipo):
        if self.buscar(placa) is not None:
            return False  # la placa ya está dentro
        nuevo = Nodo(placa, tipo)
        if self.root is None:
            self.root = nuevo
        else:
            self._insertar_recursivo(nuevo, self.root)
        return True

    def _insertar_recursivo(self, nuevo, actual):
        if nuevo.placa < actual.placa:
            if actual.left is None:
                actual.left = nuevo
            else:
                self._insertar_recursivo(nuevo, actual.left)
        else:
            if actual.right is None:
                actual.right = nuevo
            else:
                self._insertar_recursivo(nuevo, actual.right)

    # ---------- BUSCAR ----------
    def buscar(self, placa):
        actual = self.root
        while actual is not None:
            if placa == actual.placa:
                return actual
            elif placa < actual.placa:
                actual = actual.left
            else:
                actual = actual.right
        return None

    # ---------- ELIMINAR (salida de vehículo) ----------
    def eliminar(self, placa):
        self.root = self._eliminar_recursivo(self.root, placa)

    def _eliminar_recursivo(self, actual, placa):
        if actual is None:
            return None
        if placa < actual.placa:
            actual.left = self._eliminar_recursivo(actual.left, placa)
        elif placa > actual.placa:
            actual.right = self._eliminar_recursivo(actual.right, placa)
        else:
            # Caso 1 y 2: sin hijos o con un solo hijo
            if actual.left is None:
                return actual.right
            if actual.right is None:
                return actual.left
            # Caso 3: dos hijos -> se reemplaza por el menor del subárbol derecho
            sucesor = actual.right
            while sucesor.left is not None:
                sucesor = sucesor.left
            actual.placa = sucesor.placa
            actual.tipo = sucesor.tipo
            actual.hora_entrada = sucesor.hora_entrada
            actual.right = self._eliminar_recursivo(actual.right, sucesor.placa)
        return actual

    def calcular_cobro(self, nodo):
        minutos = (datetime.now() - nodo.hora_entrada).total_seconds() / 60
        horas = max(1, math.ceil(minutos / 60))  # mínimo se cobra 1 hora
        return round(minutos), horas * TARIFAS[nodo.tipo]

    # ---------- RECORRIDOS ----------
    def in_order(self, actual, lista):
        if actual is not None:
            self.in_order(actual.left, lista)
            lista.append(actual)
            self.in_order(actual.right, lista)
        return lista

    def pre_order(self, actual, lista):
        if actual is not None:
            lista.append(actual)
            self.pre_order(actual.left, lista)
            self.pre_order(actual.right, lista)
        return lista

    def post_order(self, actual, lista):
        if actual is not None:
            self.post_order(actual.left, lista)
            self.post_order(actual.right, lista)
            lista.append(actual)
        return lista

    # ---------- PROPIEDADES DEL ÁRBOL ----------
    def altura(self, actual):
        if actual is None:
            return 0
        return 1 + max(self.altura(actual.left), self.altura(actual.right))

    def peso(self, actual):
        if actual is None:
            return 0
        return 1 + self.peso(actual.left) + self.peso(actual.right)

    def hojas(self, actual, lista):
        if actual is not None:
            if actual.left is None and actual.right is None:
                lista.append(actual.placa)
            self.hojas(actual.left, lista)
            self.hojas(actual.right, lista)
        return lista

    def nivel(self, placa):
        actual, nivel = self.root, 1
        while actual is not None:
            if placa == actual.placa:
                return nivel
            actual = actual.left if placa < actual.placa else actual.right
            nivel += 1
        return None

    # ---------- Conversión a diccionario para enviarlo al frontend ----------
    def a_dict(self, actual):
        if actual is None:
            return None
        return {
            "placa": actual.placa,
            "tipo": actual.tipo,
            "entrada": actual.hora_entrada.strftime("%H:%M:%S"),
            "left": self.a_dict(actual.left),
            "right": self.a_dict(actual.right),
        }

    # ---------- Posiciones para dibujar el árbol (SVG) desde Python ----------
    def posiciones(self):
        """
        Calcula la posición (x, y) de cada nodo para dibujarlo.
        x = orden del nodo en el recorrido in-order, y = nivel del nodo.
        Devuelve nodos y líneas listos para usar en la plantilla HTML.
        """
        nodos, lineas = [], []
        contador = [0]
        ancho_col, alto_fila, margen = 112, 100, 60

        def recorrer(actual, nivel, padre_xy):
            if actual is None:
                return
            recorrer(actual.left, nivel + 1, None)  # se ajusta luego
            x = margen + contador[0] * ancho_col
            y = margen + (nivel - 1) * alto_fila
            contador[0] += 1
            if actual is self.root:
                clase = "raiz"
            elif actual.left is None and actual.right is None:
                clase = "hoja"
            else:
                clase = "rama"
            nodos.append({"placa": actual.placa, "tipo": actual.tipo,
                          "x": x, "y": y, "clase": clase, "nodo": actual})
            recorrer(actual.right, nivel + 1, None)

        recorrer(self.root, 1, None)

        # Líneas padre -> hijo
        por_nodo = {id(n["nodo"]): n for n in nodos}
        for n in nodos:
            for hijo in (n["nodo"].left, n["nodo"].right):
                if hijo is not None:
                    h = por_nodo[id(hijo)]
                    lineas.append({"x1": n["x"], "y1": n["y"], "x2": h["x"], "y2": h["y"]})

        ancho = margen * 2 + max(len(nodos) - 1, 0) * ancho_col
        alto = margen * 2 + max(self.altura(self.root) - 1, 0) * alto_fila
        for n in nodos:
            del n["nodo"]
        return {"nodos": nodos, "lineas": lineas, "ancho": ancho, "alto": alto}
