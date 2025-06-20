from PySide6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QLineEdit,
    QListWidget, QHBoxLayout, QPushButton
)
from PySide6.QtCore import Qt
from gui.multi_word_completer import MultiWordCompleter
from utils.i18n import tr
import json
import os
from PySide6.QtCore import Qt, QStringListModel
from PySide6.QtWidgets import QLabel, QListWidgetItem, QHBoxLayout, QWidget
from PySide6.QtGui import QCursor
from PySide6.QtCore import QTimer

class TagDock(QDockWidget):
    def __init__(self, db_manager, parent=None):
        super().__init__(tr("dock_tags"), parent)
        self.db = db_manager

        # Leer el límite desde el archivo de configuración
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "default_config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        self.tag_limit_list = self.config.get("tag_list_limit", 50)

        # widget principal
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(5, 5, 5, 0)
        layout.setSpacing(5)

        # --- barra de búsqueda ---
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText(tr("search_tags"))
        # callback al presionar Enter en la barra de búsqueda
        self.search_bar.returnPressed.connect(self._on_return_pressed)

        # cargar todos los tags completos
        all_tags_full = self.db.get_all_tags()
        self.all_tags = all_tags_full  # guardamos los dicts completos

        # mostrar solo los nombres para sugerencias
        tag_names = [tag["name"] for tag in all_tags_full]
        self.tag_model = QStringListModel(tag_names)

        # configurar el completer
        self.completer = MultiWordCompleter(tag_names, self.search_bar)
        self.search_bar.setCompleter(self.completer)
        # self.completer.activated.connect(self.on_completer_activated)

        self.search_bar.setCompleter(self.completer)

        # conectar señales
        self.search_bar.textEdited.connect(self.update_completer_prefix)
        self.completer.activated.connect(self.on_completer_activated)

        search_layout.addWidget(self.search_bar)

        # botón de búsqueda (sin funcionalidad)
        self.search_btn = QPushButton("🔍")
        self.search_btn.setToolTip(tr("search"))
        self.search_btn.setFixedWidth(32)
        # callback al presionar el botón de búsqueda
        self.search_btn.clicked.connect(self.emit_search_callback)
        search_layout.addWidget(self.search_btn)

        # botón de limpiar
        self.clear_btn = QPushButton("✖")
        self.clear_btn.setToolTip(tr("clear"))
        self.clear_btn.setFixedWidth(32)
        self.clear_btn.clicked.connect(self.clear_and_emit_search_callback)
        search_layout.addWidget(self.clear_btn)

        layout.addLayout(search_layout)

        # --- lista de tags ---
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # aplicar el widget principal
        self.setWidget(main_widget)

        self.load_tags_to_list(self.db.get_related_tags("", self.tag_limit_list))

        # Limitar el ancho del dock
        self.setMinimumWidth(180)
        self.setMaximumWidth(300)
        self.resize(220, self.height())  # ancho preferido

        # Opcional: evitar que los nombres largos expandan el QListWidget
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.setWordWrap(True)

    def load_tags_to_list(self, tags):
        """
        Carga la lista de tags con etiquetas cliqueables: +, -, y nombre.
        """
        self.list_widget.clear()
        for tag in tags:
            tag_name = tag["name"]

            # layout horizontal
            item_widget = QWidget()
            layout = QHBoxLayout()
            layout.setContentsMargins(5, 2, 5, 2)
            layout.setSpacing(5)

            # crear labels cliqueables
            plus_label = self._create_tag_label("+", lambda _, t=tag_name: self._append_tag_and_search(t))
            minus_label = self._create_tag_label("-", lambda _, t=tag_name: self._append_tag_and_search("-" + t))
            name_label = self._create_tag_label(tag_name, lambda _, t=tag_name: self._replace_tag_and_search(t))

            layout.addWidget(plus_label)
            layout.addWidget(minus_label)
            layout.addWidget(name_label)

            layout.addStretch()  # espacio para evitar que se vean pegados
            item_widget.setLayout(layout)

            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())

            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, item_widget)

    def _create_tag_label(self, text, callback):
        label = QLabel(text)
        label.setCursor(QCursor(Qt.PointingHandCursor))
        label.setStyleSheet("""
            QLabel {
                color: #339;
                text-decoration: underline;
            }
            QLabel:hover {
                color: #66f;
            }
        """)
        label.mousePressEvent = callback
        return label

    def _append_tag_and_search(self, tag_text):
        current_text = self.search_bar.text().strip()
        if current_text:
            new_text = current_text + " " + tag_text
        else:
            new_text = tag_text
        self.search_bar.setText(new_text)
        self.emit_search_callback()

    def _replace_tag_and_search(self, tag_text):
        self.search_bar.setText(tag_text)
        self.emit_search_callback()

    def update_completer_prefix(self, text: str):
        last_part = text.rsplit(" ", maxsplit=1)[-1]
        negated = last_part.startswith("-")
        tag_base = last_part[1:] if negated else last_part

        self.completer.setCompletionPrefix(tag_base)
        self.completer.complete()  # forzamos el filtrado interno

        count = self.completer.completionModel().rowCount()

        if len(tag_base) >= 1 and count > 0:
            rect = self.search_bar.cursorRect()
            self.completer.complete(rect)
        else:
            self.completer.popup().hide()

    def on_completer_activated(self, completion):
        def add_space():
            text = self.search_bar.text()
            if not text.endswith(" "):
                self.search_bar.setText(text + " ")
            self.search_bar.setCursorPosition(len(self.search_bar.text()))
        QTimer.singleShot(0, add_space)

    def set_on_tags_selected_callback(self, callback):
        """Permite registrar una función callback para búsqueda."""
        self._on_tags_selected_callback = callback

    def emit_search_callback(self):
        """Llama al callback registrado con el texto de la barra de búsqueda."""
        self.load_tags_to_list(self.db.get_related_tags(self.search_bar.text(), self.tag_limit_list))
        if hasattr(self, "_on_tags_selected_callback") and self._on_tags_selected_callback:
            self._on_tags_selected_callback(self.search_bar.text())

    def _on_return_pressed(self):
        # Solo dispara el callback si el popup del completer NO está visible
        if not self.completer.popup().isVisible():
            self.emit_search_callback()

    def clear_and_emit_search_callback(self):
        """Limpia la barra de búsqueda y llama al callback con texto vacío."""
        self.search_bar.clear()
        self.emit_search_callback()


