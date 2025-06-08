from PySide6.QtWidgets import QCompleter
from PySide6.QtCore import QStringListModel, Qt

class MultiWordCompleter(QCompleter):
    def __init__(self, word_list, parent=None):
        super().__init__(parent)
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterMode(Qt.MatchContains)
        self.setCompletionMode(QCompleter.PopupCompletion)

        model = QStringListModel(word_list, self)
        self.setModel(model)

        # limitar el popup a 10 elementos visibles sin scroll
        self.popup().setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.popup().setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.popup().setMaximumHeight(self.popup().sizeHintForRow(0) * 10 + 4)

    def splitPath(self, path):
        text = self.widget().text()
        cursor_pos = self.widget().cursorPosition()
        fragment = text[:cursor_pos].split(" ")[-1]
        return [fragment.lstrip("-")]

    def pathFromIndex(self, index):
        completion = super().pathFromIndex(index)
        text = self.widget().text()
        cursor_pos = self.widget().cursorPosition()

        left = text[:cursor_pos]
        right = text[cursor_pos:]

        parts = left.rsplit(" ", 1)
        if len(parts) == 2:
            before, current = parts
            neg = "-" if current.startswith("-") else ""
            new_left = f"{before} {neg}{completion}"
        else:
            new_left = f"{completion}"

        return new_left + right
