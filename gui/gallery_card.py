from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSizePolicy, QGridLayout
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal
import os

def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()

class GalleryCard(QWidget):
    def __init__(self, preview_path, booru_id, card_size=150):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignCenter)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        if os.path.exists(preview_path):
            pixmap = QPixmap(preview_path).scaled(card_size, card_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("[no image]")

        self.text_label = QLabel(str(booru_id))
        self.text_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.image_label)
        layout.addWidget(self.text_label)

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedSize(card_size + 10, card_size + 40)

    def update_grid(self):
        width = self.width() if self.width() > 0 else 800
        columns = max(1, width // (self.card_size + self.layout.spacing()))
        clear_layout(self.layout)  # Limpia correctamente el layout
        for idx, (preview_path, booru_id) in enumerate(self.previews):
            card = GalleryCard(preview_path, booru_id, self.card_size)
            row = idx // columns
            col = idx % columns
            self.layout.addWidget(card, row, col)
        self.updateGeometry()

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

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def update_grid(self):
        width = self.width() if self.width() > 0 else 800
        columns = max(1, width // (self.card_size + self.layout.spacing()))
        self.clear_layout(self.layout)  # Limpia correctamente el layout
        for idx, (preview_path, booru_id) in enumerate(self.previews):
            card = GalleryCard(preview_path, booru_id, self.card_size)
            row = idx // columns
            col = idx % columns
            self.layout.addWidget(card, row, col)
        self.updateGeometry()

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
        width = self.width() if self.width() > 0 else 800
        spacing = self.layout.spacing()
        columns = max(1, width // (self.card_size + spacing))
        rows = (len(self.previews) + columns - 1) // columns
        height = rows * (self.card_size + 40) + (rows - 1) * spacing + 10
        return QSize(width, height)