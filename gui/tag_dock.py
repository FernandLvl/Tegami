from PySide6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QLineEdit, QListWidget, QCompleter,
    QHBoxLayout, QPushButton
)
from PySide6.QtCore import Signal, Qt, QStringListModel
from utils.i18n import tr

class TagDock(QDockWidget):
    tags_selected = Signal(list)

    def __init__(self, tags, parent=None):
        super().__init__(tr("dock_tags"), parent)
        self.tags = tags
        self.tag_names = [tag['name'] if isinstance(tag, dict) else tag for tag in tags]

        # widget principal
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # --- Barra de búsqueda con botones ---
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText(tr("search_tags"))
        search_layout.addWidget(self.search_bar)

        # Botón de búsqueda
        self.search_btn = QPushButton("🔍")
        self.search_btn.setToolTip(tr("search"))
        self.search_btn.setFixedWidth(32)
        self.search_btn.clicked.connect(self.emit_selected_tags_from_search)
        search_layout.addWidget(self.search_btn)

        # Botón de limpiar
        self.clear_btn = QPushButton("✖")
        self.clear_btn.setToolTip(tr("clear"))
        self.clear_btn.setFixedWidth(32)
        self.clear_btn.clicked.connect(self.clear_search_bar)
        search_layout.addWidget(self.clear_btn)

        layout.addLayout(search_layout)

        # lista de etiquetas
        self.list_widget = QListWidget()
        self.list_widget.addItems(self.tag_names)
        self.list_widget.setSelectionMode(QListWidget.SingleSelection)
        layout.addWidget(self.list_widget)

        self.setWidget(main_widget)

        # autocompletado manual con modelo dinámico
        self.completer = QCompleter(self.tag_names)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        self.completer.setWidget(self.search_bar)
        self.completer.activated.connect(self.on_completer_activated)

        # conexiones
        self.search_bar.textEdited.connect(self.update_completer_prefix)
        self.search_bar.returnPressed.connect(self.emit_selected_tags_from_search)
        self.list_widget.itemClicked.connect(self.on_list_item_clicked)

    def clear_search_bar(self):
        """Limpia la barra de búsqueda y emite la señal para mostrar todos los previews."""
        self.search_bar.clear()
        self.update_list_selection()
        self.emit_selected_tags_from_search()

    def update_completer_prefix(self, text):
        """Actualiza el prefijo del autocompletado según el último fragmento escrito."""
        last_fragment = text.split(" ")[-1]
        self.completer.setCompletionPrefix(last_fragment)
        if last_fragment:
            # Fuerza la actualización y despliegue manual del popup del autocompletado
            rect = self.search_bar.cursorRect()
            rect.setWidth(self.completer.popup().sizeHintForColumn(0) +
                          self.completer.popup().verticalScrollBar().sizeHint().width())
            self.completer.complete(rect)

    def on_completer_activated(self, completion):
        """
        Cuando el usuario selecciona una sugerencia del autocompletado,
        reemplaza el último fragmento por el tag seleccionado y actualiza la barra.
        No dispara la búsqueda automáticamente.
        """
        text = self.search_bar.text()
        parts = text.strip().split(" ")
        parts = [p for p in parts if p]  # evita espacios múltiples o vacíos

        if parts:
            parts[-1] = completion
        else:
            parts.append(completion)

        # elimina duplicados manteniendo el orden
        seen = set()
        final = []
        for part in parts:
            if part not in seen:
                seen.add(part)
                final.append(part)

        self.search_bar.setText(" ".join(final))
        self.update_list_selection()
        # No emite búsqueda aquí

    def emit_selected_tags_from_search(self):
        """Emite la señal con la lista de tags escritos en la barra de búsqueda."""
        tags = [t for t in self.search_bar.text().strip().split() if t]
        self.tags_selected.emit(tags)

    def on_list_item_clicked(self, item):
        """
        Añade el tag seleccionado de la lista a la barra de búsqueda (sin duplicar)
        y actualiza la selección visual. No dispara la búsqueda automáticamente.
        """
        tag = item.text()
        current = self.search_bar.text().strip().split()
        if tag not in current:
            current.append(tag)
        self.search_bar.setText(" ".join(current))
        self.update_list_selection()
        # No emite búsqueda aquí

    def update_list_selection(self):
        """Actualiza la selección visual de la lista según los tags en la barra de búsqueda."""
        tags_in_search = set(self.search_bar.text().strip().split())
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setSelected(item.text() in tags_in_search)
