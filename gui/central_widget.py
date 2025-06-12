from PySide6.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QAbstractItemView, QSizePolicy, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, QSize
from .gallery_card import GalleryCard
from PySide6.QtGui import QPixmap, QIcon
import os

class GalleryListWidget(QListWidget):
    def __init__(self, previews, card_size=150, parent=None):
        super().__init__(parent)
        self.previews = previews
        self.card_size = card_size
        self.setViewMode(QListWidget.IconMode)
        self.setResizeMode(QListWidget.Adjust)
        self.setMovement(QListWidget.Static)
        self.setSpacing(10)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setIconSize(QSize(1, 1))  # hack: evita el reescalado automático
        self.create_card()
        self.update_cards()

    def update_cards(self):
        # actualizar el tamaño de las tarjetas
        for i in range(self.count()):
            item = self.item(i)
            card = self.itemWidget(item)
            if card:
                card.setFixedSize(self.card_size + 10, self.card_size + 40)
                card.image_label.setFixedSize(self.card_size, self.card_size)
                card.text_label.setFixedWidth(self.card_size)
                card.updateGeometry()
            item.setSizeHint(card.sizeHint())
            item.setSizeHint(QSize(self.card_size + 10, self.card_size + 40))
        self.updateGeometry()
        self.setIconSize(QSize(self.card_size, self.card_size))
        self.setGridSize(QSize(self.card_size + 10, self.card_size + 40))

    def create_card(self):
        for preview_path, booru_id in self.previews:
            card = GalleryCard(preview_path, booru_id, self.card_size)
            item = QListWidgetItem()
            item.setSizeHint(card.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, card)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            new_size = self.card_size + (10 if delta > 0 else -10)
            new_size = max(50, min(400, new_size))
            if new_size != self.card_size:
                self.card_size = new_size
                self.update_cards()
            event.accept()
        else:
            super().wheelEvent(event)

def create_grid_view(previews, card_size=150, on_card_size_change=None, parent=None):
    container = GalleryListWidget(previews, card_size, parent)
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
            icon = QIcon("resources/image-not-found.png")
            label.setPixmap(icon.pixmap(thumb_size, thumb_size))
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