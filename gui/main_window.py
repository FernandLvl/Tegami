import json
from PySide6.QtWidgets import (
    QMainWindow, QTextEdit, QDockWidget, QListWidget,
    QLabel, QStatusBar, QMenuBar, QMenu, QWidget, QVBoxLayout, QScrollArea, QHBoxLayout,
    QPushButton, QSizePolicy, QToolBar  # <-- agrega QToolBar aquí
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QAction
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from PySide6.QtSvg import QSvgRenderer
from utils.i18n import tr
from config.config import get_setting  # ← Solo get_setting, save_setting se usa solo en _save_config
from .central_widget import create_grid_view, create_list_view
import os
from PySide6.QtGui import QPixmap, QPainter, QIcon
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import QSize, Qt
import sqlite3
from database.db_manager import DBManager
from gui.tag_dock import TagDock
from gui.about_dialog import AboutDialog
from boorus.e621_sync import e621_save_json



CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(CURRENT_DIR, "..", "resources", "icons")
SOUND_PATH = os.path.join(CURRENT_DIR, "..", "resources", "sounds")
DB_PATH = os.path.join(CURRENT_DIR, "..", "data", "gallery.db")



class MainWindow(QMainWindow):

    # --------------------
    # inicialización
    # --------------------
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tegami v0.1")
        self.setWindowIcon(QIcon("resources/logo.png"))

        self.tag_dock = None
        self.console_dock = None
        self._is_closing = False

        # Instancia el gestor de base de datos
        self.db = DBManager(DB_PATH)
        self.previews = self.db.get_all_previews()

        # Tamaño de tarjeta configurable
        self.card_size = self._get_setting("card_size") or 150

        # orden correcto de creación
        self._create_status_bar()
        self._create_central_widget()
        self._create_dock_widgets()      # ← primero los docks
        self._create_menu_bar()          # ← luego el menú
        self._create_toolbar()           # ← agrega el toolbar después del menú

        # restaurar geometría y estado si existen
        geometry = self._get_setting("window_geometry")
        state = self._get_setting("window_state")

        if geometry:
            from PySide6.QtCore import QByteArray
            self.restoreGeometry(QByteArray.fromBase64(geometry.encode()))
        else:
            self.resize(1200, 600)

        if state:
            self.restoreState(QByteArray.fromBase64(state.encode()))
        
        # self.test_guardar_e621()
        # self.db.get_preview_page(1, 100)



    # --------------------
    # creación de interfaz
    # --------------------
    def _create_menu_bar(self):
        menu_bar = self.menuBar()

        # menú Archivo
        archivo_menu = menu_bar.addMenu(tr("menu_file"))
        abrir_action = QAction(tr("menu_open"), self)
        salir_action = QAction(tr("menu_exit"), self)
        salir_action.triggered.connect(self.close)

        archivo_menu.addAction(abrir_action)
        archivo_menu.addSeparator()
        archivo_menu.addAction(salir_action)

        # menú Editar
        editar_menu = menu_bar.addMenu(tr("menu_edit"))
        cortar_action = QAction(tr("menu_cut"), self)
        copiar_action = QAction(tr("menu_copy"), self)
        pegar_action = QAction(tr("menu_paste"), self)

        editar_menu.addAction(cortar_action)
        editar_menu.addAction(copiar_action)
        editar_menu.addAction(pegar_action)

        # menú view
        view_menu = menu_bar.addMenu(tr("menu_view"))
        #logica para ocultar o mostrar dockss
        
        # menú Ventana
        window_menu = menu_bar.addMenu(tr("menu_window"))

        self.toggle_tag_dock_action = QAction(tr("menu_show_tags"), self, checkable=True)
        self.toggle_tag_dock_action.setChecked(True)
        self.toggle_tag_dock_action.toggled.connect(
            lambda checked: self.tag_dock.setVisible(checked)
        )

        self.toggle_console_dock_action = QAction(tr("menu_show_console"), self, checkable=True)
        self.toggle_console_dock_action.setChecked(True)
        self.toggle_console_dock_action.toggled.connect(
            lambda checked: self.console_dock.setVisible(checked)
        )

        # sincronizar estado si docks se cierran manualmente
        self.tag_dock.visibilityChanged.connect(self.toggle_tag_dock_action.setChecked)
        self.console_dock.visibilityChanged.connect(self.toggle_console_dock_action.setChecked)

        window_menu.addAction(self.toggle_tag_dock_action)
        window_menu.addAction(self.toggle_console_dock_action)

        # menú Ayuda
        ayuda_menu = menu_bar.addMenu(tr("menu_help"))
        acerca_action = QAction(tr("menu_about"), self)
        acerca_action.triggered.connect(self.show_about_dialog)
        ayuda_menu.addAction(acerca_action)

    def _create_dock_widgets(self):
        # dock lateral izquierdo para filtros por tag
        self.tag_dock = TagDock(self.db, self)
        self.tag_dock.setObjectName("TagDock")
        self.addDockWidget(Qt.LeftDockWidgetArea, self.tag_dock)
        # self.tag_dock.tags_selected.connect(self.on_tags_selected)

        # dock inferior para mensajes o consola
        self.console_dock = QDockWidget(tr("dock_console"), self)
        self.console_dock.setObjectName("ConsoleDock")
        console_text = QTextEdit()
        console_text.setReadOnly(True)
        console_text.setPlainText(tr("console_placeholder"))
        self.console_dock.setWidget(console_text)
        self.console_dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console_dock)

    def _create_status_bar(self):
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage(tr("status_ready"))

        # contenedor para los botones
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)

        # Rutas absolutas para los iconos
        # (Ya están definidas como constantes arriba)

        # botón para vista de lista
        self.list_view_btn = QPushButton()
        self.list_view_btn.setIcon(QIcon(os.path.join(ICON_PATH, "list-ul-solid.svg")))
        self.list_view_btn.setToolTip(tr("tooltip_list_view"))
        self.list_view_btn.setIconSize(QSize(16, 16))

        # botón para vista de cuadrícula
        self.grid_view_btn = QPushButton()
        self.grid_view_btn.setIcon(QIcon(os.path.join(ICON_PATH, "image-solid.svg")))
        self.grid_view_btn.setToolTip(tr("tooltip_grid_view"))
        self.grid_view_btn.setIconSize(QSize(16, 16))

        # añadir botones al layout
        button_layout.addWidget(self.list_view_btn)
        button_layout.addWidget(self.grid_view_btn)

        # usar un spacer para empujar a la derecha
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.status.addPermanentWidget(spacer)

        # conectar botones a las funciones de cambio de vista
        self.list_view_btn.clicked.connect(lambda: self.switch_view("list"))
        self.grid_view_btn.clicked.connect(lambda: self.switch_view("grid", self.current_card_size))  # o el tamaño que desees

        # añadir el contenedor de botones al status bar
        self.status.addPermanentWidget(button_container)

    def _create_central_widget(self):
        self.current_view = "grid"
        self.current_card_size = self.card_size
        gallery_widget = create_grid_view(
            self.previews,
            self.card_size,
            self._on_card_size_change
        )
        self.setCentralWidget(gallery_widget)

    def _create_toolbar(self):
        toolbar = QToolBar("Barra de herramientas", self)
        toolbar.setMovable(True)
        toolbar.setFloatable(True)
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)

        # Botón de nuevo (demostrativo)
        new_action = QAction(QIcon(os.path.join(ICON_PATH, "plus-solid.svg")), tr("toolbar_new"), self)
        toolbar.addAction(new_action)

        self.mode_action = QAction(QIcon("resources/icons/cloud-off.svg"), "Modo Offline", self)
        self.mode_action.setCheckable(True)
        self.mode_action.setChecked(False)
        self.mode_action.triggered.connect(self.toggle_mode)
        toolbar.addAction(self.mode_action)


    # --------------------
    # slots / callbacks
    # --------------------
    # def on_tags_selected(self, selected_tags):
    #     # Si selected_tags es una lista de diccionarios, extrae los nombres
    #     tag_names = [tag['name'] if isinstance(tag, dict) else tag for tag in selected_tags]
    #     filtered_previews = self.db.get_previews_by_tags(tag_names)
    #     self.previews = filtered_previews
    #     self.reload_central_view()

    def reload_central_view(self, card_size=None):
        if card_size is None:
            card_size = self.current_card_size
        if self.current_view == "grid":
            widget = create_grid_view(
                self.previews,
                card_size,
                self._on_card_size_change
            )
        else:
            widget = create_list_view(self.previews)
        self.setCentralWidget(widget)

    def switch_view(self, view_type, card_size=None):
        if card_size is None:
            card_size = self.current_card_size
        if view_type != self.current_view or card_size != self.current_card_size:
            self.current_view = view_type
            self.current_card_size = card_size
            self.reload_central_view(card_size)

    def load_previews_from_db(self):
        db_path = "data/gallery.db"
        previews = []
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT preview_path, booru_id FROM resources")
            previews = cursor.fetchall()
            conn.close()
        except Exception as e:
            print(f"Error al cargar la base de datos: {e}")
        return previews

    def show_about_dialog(self):
        dlg = AboutDialog(self)
        dlg.exec()

    def toggle_mode(self):
        if self.mode_action.isChecked():
            # Cambiar a online
            self.mode_action.setIcon(QIcon("resources/icons/cloud.svg"))
            self.mode_action.setText("Modo Online")
            self.show_booru_selector()
        else:
            # Cambiar a offline
            self.mode_action.setIcon(QIcon("resources/icons/cloud-off.svg"))
            self.mode_action.setText("Modo Offline")
            # Oculta paneles online, muestra solo offline


    # --------------------
    # lógica interna / utilidades
    # --------------------

    def closeEvent(self, event):
        # guardar geometría y estado de la ventana
        self._save_config("window_geometry", self.saveGeometry().toBase64().data().decode())
        self._save_config("window_state", self.saveState().toBase64().data().decode())
        self._save_config("start_maximized", self.isMaximized())
        self._is_closing = True
        super().closeEvent(event)

    def _toggle_dock(self, dock, config_key, checked):
        if dock is not None:
            dock.setVisible(checked)
            self._save_config(config_key, checked)
    
    def _on_card_size_change(self, new_size):
        self.current_card_size = new_size
        self._save_config("card_size", new_size)

    def _save_config(self, key, value):
        if key is None:
            return  # evita errores tontos
        from config.config import save_setting
        save_setting(key, value)

    def _get_setting(self, key):
        from config.config import get_setting
        return get_setting(key)

    def resizeEvent(self, event):
        # Solo guarda el tamaño si la ventana NO está maximizada
        if not self.isMaximized():
            size = {"width": self.width(), "height": self.height()}
            self._save_config("window_size", size)
            self._save_config("start_maximized", False)
        super().resizeEvent(event)



    def test_guardar_e621(self):
            json_path = "tests/e621.json"
            db_path = "data/gallery.db"  # ajusta según tu ruta real

            # cargar json
            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)

            # guardar en la base de datos
            e621_save_json(json_data, db_path)

            print("Datos guardados correctamente desde e621.json")