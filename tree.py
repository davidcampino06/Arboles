"""
Binary Search Tree (BST) for a parking lot.
Each node is a vehicle and the tree is ordered by LICENSE PLATE (alphabetical order).
"""
from datetime import datetime
import math

# Hourly rates (charged per hour or fraction of an hour)
RATES = {"car": 4000, "motorcycle": 2000}


class Node:
    def __init__(self, plate, vehicle_type):
        self.plate = plate
        self.vehicle_type = vehicle_type
        self.entry_time = datetime.now()
        self.left = None
        self.right = None


class ParkingLot:
    def __init__(self):
        self.root = None

    # ---------- INSERT (vehicle entry) ----------
    def insert(self, plate, vehicle_type):
        if self.search(plate) is not None:
            return False  # the plate is already inside
        new_node = Node(plate, vehicle_type)
        if self.root is None:
            self.root = new_node
        else:
            self._insert_recursive(new_node, self.root)
        return True

    def _insert_recursive(self, new_node, current):
        if new_node.plate < current.plate:
            if current.left is None:
                current.left = new_node
            else:
                self._insert_recursive(new_node, current.left)
        else:
            if current.right is None:
                current.right = new_node
            else:
                self._insert_recursive(new_node, current.right)

    # ---------- SEARCH ----------
    def search(self, plate):
        current = self.root
        while current is not None:
            if plate == current.plate:
                return current
            elif plate < current.plate:
                current = current.left
            else:
                current = current.right
        return None

    # ---------- DELETE (vehicle exit) ----------
    def delete(self, plate):
        self.root = self._delete_recursive(self.root, plate)

    def _delete_recursive(self, current, plate):
        if current is None:
            return None
        if plate < current.plate:
            current.left = self._delete_recursive(current.left, plate)
        elif plate > current.plate:
            current.right = self._delete_recursive(current.right, plate)
        else:
            # Cases 1 and 2: no children or only one child
            if current.left is None:
                return current.right
            if current.right is None:
                return current.left
            # Case 3: two children -> replace with the smallest node of the right subtree
            successor = current.right
            while successor.left is not None:
                successor = successor.left
            current.plate = successor.plate
            current.vehicle_type = successor.vehicle_type
            current.entry_time = successor.entry_time
            current.right = self._delete_recursive(current.right, successor.plate)
        return current

    def calculate_fee(self, node):
        minutes = (datetime.now() - node.entry_time).total_seconds() / 60
        hours = max(1, math.ceil(minutes / 60))  # at least 1 hour is charged
        return round(minutes), hours * RATES[node.vehicle_type]

    # ---------- TRAVERSALS ----------
    def in_order(self, current, result):
        if current is not None:
            self.in_order(current.left, result)
            result.append(current)
            self.in_order(current.right, result)
        return result

    def pre_order(self, current, result):
        if current is not None:
            result.append(current)
            self.pre_order(current.left, result)
            self.pre_order(current.right, result)
        return result

    def post_order(self, current, result):
        if current is not None:
            self.post_order(current.left, result)
            self.post_order(current.right, result)
            result.append(current)
        return result

    # ---------- TREE PROPERTIES ----------
    def height(self, current):
        if current is None:
            return 0
        return 1 + max(self.height(current.left), self.height(current.right))

    def weight(self, current):
        """Number of nodes in the tree (number of parked vehicles)."""
        if current is None:
            return 0
        return 1 + self.weight(current.left) + self.weight(current.right)

    def leaves(self, current, result):
        if current is not None:
            if current.left is None and current.right is None:
                result.append(current.plate)
            self.leaves(current.left, result)
            self.leaves(current.right, result)
        return result

    def level(self, plate):
        current, level = self.root, 1
        while current is not None:
            if plate == current.plate:
                return level
            current = current.left if plate < current.plate else current.right
            level += 1
        return None

    # ---------- Node positions to draw the tree (SVG) from Python ----------
    def layout(self):
        """
        Calculates the (x, y) position of each node to draw it.
        x = order of the node in the in-order traversal, y = level of the node.
        Returns nodes and edges ready to be used in the HTML template.
        """
        nodes, edges = [], []
        counter = [0]
        column_width, row_height, margin = 112, 100, 60

        def visit(current, level):
            if current is None:
                return
            visit(current.left, level + 1)
            x = margin + counter[0] * column_width
            y = margin + (level - 1) * row_height
            counter[0] += 1
            if current is self.root:
                role = "root"
            elif current.left is None and current.right is None:
                role = "leaf"
            else:
                role = "branch"
            nodes.append({"plate": current.plate, "vehicle_type": current.vehicle_type,
                          "x": x, "y": y, "role": role, "node": current})
            visit(current.right, level + 1)

        visit(self.root, 1)

        # Edges parent -> child
        by_node = {id(n["node"]): n for n in nodes}
        for n in nodes:
            for child in (n["node"].left, n["node"].right):
                if child is not None:
                    c = by_node[id(child)]
                    edges.append({"x1": n["x"], "y1": n["y"], "x2": c["x"], "y2": c["y"]})

        width = margin * 2 + max(len(nodes) - 1, 0) * column_width
        height = margin * 2 + max(self.height(self.root) - 1, 0) * row_height
        for n in nodes:
            del n["node"]
        return {"nodes": nodes, "edges": edges, "width": width, "height": height}
