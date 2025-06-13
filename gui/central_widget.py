from PySide6.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QAbstractItemView, QSizePolicy, QListWidget, QListWidgetItem, QFrame, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, QSize
from .gallery_card import GalleryCard
from PySide6.QtGui import QPixmap, QIcon
from config.config import get_setting
import os

class GalleryListWidget(QListWidget):
    def __init__(self, previews, card_size=150, parent=None):
        super().__init__(parent)
        self.previews = previews
        self.card_size = card_size
        self.missing_previews = []
        self.setViewMode(QListWidget.IconMode)
        self.setResizeMode(QListWidget.Adjust)
        self.setMovement(QListWidget.Static)
        self.setSpacing(10)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setIconSize(QSize(1, 1))
        self.create_cards()
        self.update_cards()

    def update_cards(self):
        for i in range(self.count()):
            item = self.item(i)
            card = self.itemWidget(item)
            if card:
                card.update_card_size(self.card_size)
                item.setSizeHint(card.sizeHint())
        self.updateGeometry()
        self.setIconSize(QSize(self.card_size, self.card_size))
        self.setGridSize(QSize(self.card_size + 10, self.card_size + 40))

    def create_cards(self):
            for preview_path, booru_id, source in self.previews:
                if os.path.exists(preview_path):
                    image_path = preview_path
                else:
                    image_path = "resources/image-not-found.png"
                    self.missing_previews.append((preview_path, booru_id, source))
                card = GalleryCard(image_path, booru_id, self.card_size)
                item = QListWidgetItem()
                item.setSizeHint(card.sizeHint())
                self.addItem(item)
                self.setItemWidget(item, card)
            # if self.missing_previews:
                # print("missing_previews size:", len(self.missing_previews))

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            new_size = self.card_size + (10 if delta > 0 else -10)
            new_size = max(50, min(400, new_size))
            if new_size != self.card_size:
                self.card_size = new_size
                self._save_config("card_size", new_size)
                self.update_cards()
            event.accept()
        else:
            super().wheelEvent(event)

    def _save_config(self, key, value):
        if key is None:
            return  # evita errores tontos
        from config.config import save_setting
        save_setting(key, value)

def create_grid_view(previews, card_size=150, current_page=1, total_pages=1, on_page_change=None, on_missing_previews=None, parent=None):
    container = QWidget()
    layout = QVBoxLayout(container)

    gallery_widget = GalleryListWidget(previews, card_size, parent)

    # si se pasó un callback y hay previews faltantes, llamarlo
    if on_missing_previews and gallery_widget.missing_previews:
        on_missing_previews(gallery_widget.missing_previews)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(gallery_widget)
    layout.addWidget(scroll)

    if on_page_change is not None:
        nav_bar = create_navigation_bar(current_page, total_pages, on_page_change)
        layout.addWidget(nav_bar)

    return container

def create_list_view(previews, current_page=1, total_pages=1, on_page_change=None, on_missing_previews=None):
    thumb_size = 64
    missing_previews = []

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

    for row, (preview_path, booru_id, source) in enumerate(previews):
        label = QLabel()
        label.setAlignment(Qt.AlignCenter)

        if os.path.exists(preview_path):
            pixmap = QPixmap(preview_path).scaled(
                thumb_size, thumb_size,
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            label.setPixmap(pixmap)
        else:
            icon = QIcon("resources/image-not-found.png")
            label.setPixmap(icon.pixmap(thumb_size, thumb_size))
            missing_previews.append((preview_path, booru_id, source))

        table.setCellWidget(row, 0, label)
        table.setItem(row, 1, QTableWidgetItem(str(booru_id)))
        table.setItem(row, 2, QTableWidgetItem(preview_path))

    table.resizeColumnsToContents()
    table.setMinimumHeight(thumb_size * 4)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(table)

    container = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(5, 5, 5, 5)
    layout.setSpacing(10)
    layout.addWidget(scroll)

    if on_page_change:
        nav_bar = create_navigation_bar(current_page, total_pages, on_page_change)
        layout.addWidget(nav_bar)

    container.setLayout(layout)

    # callback si hay previews faltantes
    if on_missing_previews and missing_previews:
        on_missing_previews(missing_previews)

    return container

def create_navigation_bar(current_page, total_pages, on_page_change):
    frame = QFrame()
    layout = QHBoxLayout()
    layout.setAlignment(Qt.AlignCenter)
    layout.setSpacing(5)

    def make_button(label, page, enabled=True):
        btn = QPushButton(label)
        btn.setEnabled(enabled)
        btn.clicked.connect(lambda: on_page_change(page))
        return btn

    # botones de navegación directa
    layout.addWidget(make_button("<<", 1, current_page > 1))
    layout.addWidget(make_button("<", current_page - 1, current_page > 1))

    def add_ellipsis():
        el = QLabel("...")
        el.setStyleSheet("font-weight: bold; padding: 0 4px;")
        layout.addWidget(el)

    # siempre mostrar la primera página
    layout.addWidget(make_button(str(1), 1, current_page != 1))

    # definir el rango de páginas centrales
    side_pages = get_setting("ellipsis_side_pages")
    start = max(2, current_page - side_pages)
    end = min(total_pages - 1, current_page + side_pages)

    # si hay separación entre la primera y el inicio del bloque
    if start > 2:
        add_ellipsis()

    for i in range(start, end + 1):
        layout.addWidget(make_button(str(i), i, current_page != i))

    # si hay separación entre el final del bloque y la última
    if end < total_pages - 1:
        add_ellipsis()

    # mostrar última página (si hay más de una página)
    if total_pages > 1:
        layout.addWidget(make_button(str(total_pages), total_pages, current_page != total_pages))

    # botones de navegación directa
    layout.addWidget(make_button(">", current_page + 1, current_page < total_pages))
    layout.addWidget(make_button(">>", total_pages, current_page < total_pages))

    frame.setLayout(layout)
    return frame