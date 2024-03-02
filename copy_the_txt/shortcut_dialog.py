from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence

class ShortcutDialog(QDialog):
    shortcutSet = pyqtSignal(str)  # 단축키가 설정되었을 때 발생할 신호

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Set Shortcut')
        self.layout = QVBoxLayout(self)
        
        self.infoLabel = QLabel("Press the key combination you want to set as a shortcut, then click 'Set'.")
        self.layout.addWidget(self.infoLabel)
        
        self.shortcutLineEdit = QLineEdit(self)
        self.shortcutLineEdit.setPlaceholderText("Shortcut will appear here")
        self.shortcutLineEdit.setReadOnly(True)  # 사용자가 직접 입력하는 것을 방지
        self.layout.addWidget(self.shortcutLineEdit)
        
        self.setButton = QPushButton("Set", self)
        self.setButton.clicked.connect(self.onSetClicked)
        self.layout.addWidget(self.setButton)
        
        self.keySequence = None  # 키 시퀀스를 저장할 변수

    def keyPressEvent(self, event):
        modifiers = event.modifiers()
        key = event.key()

        # 수정자를 문자열로 변환
        modifierKeys = ''
        if modifiers & Qt.ShiftModifier:
            modifierKeys += 'Shift+'
        if modifiers & Qt.ControlModifier:
            modifierKeys += 'Ctrl+'
        if modifiers & Qt.AltModifier:
            modifierKeys += 'Alt+'
        if modifiers & Qt.MetaModifier:
            modifierKeys += 'Meta+'

        # 키 값을 문자열로 변환 (QKeySequence를 사용하여)
        keyText = QKeySequence(key).toString()

        # 최종 단축키 문자열 생성
        self.keySequence = modifierKeys + keyText

        # QLineEdit 위젯에 표시
        self.shortcutLineEdit.setText(self.keySequence)

    def onSetClicked(self):
        # 'Set' 버튼 클릭 시 신호를 발생시키고 대화상자를 닫음
        # 사용자가 아무 입력도 하지 않았을 경우 단축키를 삭제한다는 의미로 None을 전달
        self.shortcutSet.emit(self.keySequence if self.keySequence else None)
        self.accept()