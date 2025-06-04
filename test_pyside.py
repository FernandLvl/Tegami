from PySide6.QtWidgets import QApplication, QMainWindow, QAction

app = QApplication([])

window = QMainWindow()
menu = window.menuBar().addMenu("Archivo")

# prueba simple de QAction
action = QAction("Salir", window)
menu.addAction(action)

window.show()
app.exec()
