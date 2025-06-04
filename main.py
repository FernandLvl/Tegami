import sys
from PySide6.QtWidgets import QApplication
from config.config import load_config
from config.config import get_current_language
from gui.main_window import MainWindow
from utils.i18n import load_language
from utils.theme import apply_theme

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # cargar todas las configuraciones
    config = load_config()

    # establecer el idioma actual
    language = get_current_language()
    load_language(language)

    # establecer el tema actual
    apply_theme()

    # abrir ventana principal
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
