from PySide6.QtWidgets import QApplication
from config.config import get_setting
from pathlib import Path

def apply_theme():
    theme_name = get_setting("theme")
    theme_file = Path(f"themes/{theme_name}.qss")

    if theme_file.exists():
        with open(theme_file, "r", encoding="utf-8") as f:
            style = f.read()
            QApplication.instance().setStyleSheet(style)
    else:
        print(f"[aviso] tema '{theme_name}' no encontrado")
