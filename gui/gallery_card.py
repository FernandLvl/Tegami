from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSizePolicy, QGridLayout
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal, QSize
import os

def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()

class GalleryCard(QWidget):
    def __init__(self, image_path, booru_id, card_size=150):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignCenter)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        pixmap = QPixmap(image_path).scaled(
            card_size, card_size,
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.image_label.setPixmap(pixmap)

        self.text_label = QLabel(str(booru_id))
        self.text_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.image_label)
        layout.addWidget(self.text_label)

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedSize(card_size + 10, card_size + 40)
