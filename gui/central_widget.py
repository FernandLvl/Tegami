# gui/central_widget.py

from PySide6.QtWidgets import QWidget, QGridLayout, QScrollArea, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QAbstractItemView
from PySide6.QtCore import Qt, Signal, QSize
from .gallery_card import GalleryCard
from PySide6.QtGui import QPixmap
import os

class GridContainer(QWidget):
    card_size_changed = Signal(int)

    def __init__(self, previews, card_size=150, on_card_size_change=None, parent=None):
        super().__init__(parent)
        self.previews = previews
        self.card_size = card_size
        self.on_card_size_change = on_card_size_change
        self.layout = QGridLayout(self)
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.layout.setSpacing(10)
        self.setMouseTracking(True)
        self.update_grid()

    def update_grid(self):
        width = self.width() if self.width() > 0 else 800
        columns = max(1, width // (self.card_size + self.layout.spacing()))
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
        for idx, (preview_path, booru_id) in enumerate(self.previews):
            card = GalleryCard(preview_path, booru_id, self.card_size)
            row = idx // columns
            col = idx % columns
            self.layout.addWidget(card, row, col)
        self.updateGeometry()  # <-- importante para recalcular el tamaño

    def resizeEvent(self, event):
        self.update_grid()
        super().resizeEvent(event)

    def wheelEvent(self, event):
        if self.underMouse() and event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            new_size = self.card_size + (10 if delta > 0 else -10)
            new_size = max(50, min(400, new_size))
            if new_size != self.card_size:
                self.card_size = new_size
                if self.on_card_size_change:
                    self.on_card_size_change(new_size)
                self.update_grid()
            event.accept()
        else:
            super().wheelEvent(event)

    def sizeHint(self):
        # Calcula columnas igual que en update_grid
        width = self.width() if self.width() > 0 else 800
        spacing = self.layout.spacing()
        columns = max(1, width // (self.card_size + spacing))
        rows = (len(self.previews) + columns - 1) // columns
        # Alto total = filas * alto de tarjeta + espacios
        height = rows * (self.card_size + 40) + (rows - 1) * spacing + 10
        # Ancho total = igual que el ancho actual
        return QSize(width, height)

def create_grid_view(previews, card_size=150, on_card_size_change=None, parent=None):
    container = GridContainer(previews, card_size, on_card_size_change, parent)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(container)
    return scroll

def create_list_view(previews):
    table = QTableWidget()
    table.setColumnCount(3)
    table.setHorizontalHeaderLabels(["Miniatura", "ID", "Ruta"])
    table.setRowCount(len(previews))
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setStretchLastSection(True)
    table.setShowGrid(False)
    table.setAlternatingRowColors(True)

    thumb_size = 64

    for row, (preview_path, booru_id) in enumerate(previews):
        # Miniatura
        label = QLabel()
        label.setAlignment(Qt.AlignCenter)
        if os.path.exists(preview_path):
            pixmap = QPixmap(preview_path).scaled(thumb_size, thumb_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(pixmap)
        else:
            label.setText("[no image]")
        table.setCellWidget(row, 0, label)

        # ID
        table.setItem(row, 1, QTableWidgetItem(str(booru_id)))
        # Ruta
        table.setItem(row, 2, QTableWidgetItem(preview_path))

    table.resizeColumnsToContents()
    table.setMinimumHeight(thumb_size * 4)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(table)
    return scroll