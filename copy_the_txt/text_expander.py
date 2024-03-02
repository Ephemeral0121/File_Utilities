from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QTextEdit, QPushButton
from PyQt5.QtCore import QPoint, pyqtSignal

class TextExpander(QDialog):
    shortcutUpdated = pyqtSignal(str)
    def __init__(self, text, parentButton=None, parent=None):
        super().__init__(parent)
        self.parentButton = parentButton
        self.setWindowTitle("Expanded Text")
        self.initUI(text)

    def initUI(self, text):
        layout = QVBoxLayout()

        self.titleEdit = QLineEdit(self)
        self.titleEdit.setPlaceholderText('Enter title here...')
        self.titleEdit.setClearButtonEnabled(True)
        self.titleEdit.textChanged.connect(self.updateTitle)

        if self.parentButton and self.parentButton.title:
            self.titleEdit.setText(self.parentButton.title)

        layout.addWidget(self.titleEdit)

        self.textEdit = QTextEdit(self)
        self.textEdit.setText(text)
        layout.addWidget(self.textEdit)

        self.modifyButton = QPushButton('Modify', self)
        self.modifyButton.clicked.connect(self.modifyText)
        layout.addWidget(self.modifyButton)

        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 14px;
                margin: 1px;
                text-align: left;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #43A047;
            }
        """)

        self.setLayout(layout)

    def updateTitle(self, title):
        if self.parentButton:
            self.parentButton.updateTitle(title)

    def modifyText(self):
        modifiedText = self.textEdit.toPlainText()
        if self.parentButton:
            self.parentButton.updateText(modifiedText)

    def adjustPosition(self, parent):
        if parent:
            parentPos = parent.mapToGlobal(QPoint(0, 0))
            self.move(parentPos.x() + parent.width(), parentPos.y())
            self.resize(parent.size())

    def closeEvent(self, event):
        if self.parentButton and not self.parentButton.isDeleted:
            self.parentButton.expandButton.setText('▶')
            self.parentButton.expander = None
        event.accept()