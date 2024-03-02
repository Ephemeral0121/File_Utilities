import keyboard
import uuid
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QSizePolicy, QHBoxLayout, QMessageBox)
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QEvent, QMimeData
from PyQt5.QtGui import QFontMetrics, QDrag

from .shortcut_dialog import ShortcutDialog
from .text_expander import TextExpander

registered_shortcuts = {}

class CustomEvent(QEvent):
    def __init__(self, text):
        super().__init__(QEvent.Type(QEvent.User + 1))
        self.text = text

class TextButton(QWidget):
    copyRequested = pyqtSignal(str)
    def __init__(self, text, app, parent=None):
        super().__init__(parent)
        self.id = str(uuid.uuid4())
        self.originalText = text
        self.app = app
        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        self.expander = None
        self.isDeleted = False

        self.title = ""

        self.dragStartPosition = QPoint()

        self.textButton = QPushButton()
        self.textButton.clicked.connect(self.copyText)
        self.layout.addWidget(self.textButton, 1)

        self.deleteButton = QPushButton('✖')
        self.deleteButton.setFixedWidth(50)
        self.deleteButton.clicked.connect(self.deleteSelf)
        self.layout.addWidget(self.deleteButton)

        self.expandButton = QPushButton('▶')
        self.expandButton.setFixedWidth(50)
        self.expandButton.clicked.connect(self.toggleExpand)
        self.layout.addWidget(self.expandButton)

        self.shortcutButton = QPushButton('Set Shortcut')
        self.shortcutButton.clicked.connect(self.setShortcut)
        self.layout.addWidget(self.shortcutButton)
        self.shortcut = None  # 단축키 저장을 위한 변수
        self.shortcutRegistered = False  # 단축키 등록 여부를 추적하는 변수

        # shortcutButton의 크기 정책 설정
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.shortcutButton.setSizePolicy(sizePolicy)
        self.shortcutButton.setFixedWidth(140)  # shortcutButton에 고정된 너비 설정

        self.textButton.setText(text)
        self.updateButtonText()
        self.copyRequested.connect(self.copyText)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragStartPosition = event.pos()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.pos() - self.dragStartPosition).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mimeData = QMimeData()
        mimeData.setText(self.id)  # 위젯 ID를 mimeData에 설정
        drag.setMimeData(mimeData)
        drag.exec_(Qt.MoveAction)

    def setShortcut(self):
        dialog = ShortcutDialog(self)
        dialog.shortcutSet.connect(self.registerShortcut)  # 단축키 설정 신호를 처리할 슬롯 연결
        dialog.exec_()

    def registerShortcut(self, shortcut):
        global registered_shortcuts

        # 단축키가 이미 등록된 경우 해당 단축키 제거
        if shortcut in registered_shortcuts:
            other_button_id = registered_shortcuts[shortcut]
            if other_button_id != self.id:
                other_button = self.app.findButtonById(other_button_id)
                if other_button:
                    other_button.removeShortcut()

        # 이전에 설정된 단축키 제거
        if self.shortcutRegistered and self.shortcut:
            try:
                keyboard.remove_hotkey(self.shortcut)
            except KeyError:  # 단축키가 이미 제거되었거나 등록되지 않은 경우
                pass
            del registered_shortcuts[self.shortcut]

        # 새 단축키 등록
        if shortcut:
            self.shortcut = shortcut
            keyboard.add_hotkey(shortcut, lambda: self.handleShortcut())
            registered_shortcuts[shortcut] = self.id
            self.shortcutRegistered = True
            self.shortcutButton.setText(f'{shortcut}')
        else:
            self.shortcut = None
            self.shortcutRegistered = False
            self.shortcutButton.setText('Set Shortcut')

    def removeShortcut(self):
        if self.shortcutRegistered and self.shortcut:
            try:
                keyboard.remove_hotkey(self.shortcut)
            except KeyError:
                pass
            del registered_shortcuts[self.shortcut]
            self.shortcut = None
            self.shortcutRegistered = False
            self.shortcutButton.setText('Set Shortcut')

    def handleShortcut(self):
        customEvent = CustomEvent(self.originalText)
        QApplication.postEvent(self.app, customEvent)



    def deleteSelf(self):
        if self.shortcut:
            keyboard.remove_hotkey(self.shortcut)  # 위젯이 삭제될 때 전역 단축키 해제
        if self.expander and self.expander.isVisible():
            self.expander.close()
            self.expander = None
        self.isDeleted = True
        self.deleteLater()

    def updateTitle(self, title):
        self.title = title
        self.updateButtonText()
        self.app.saveData()

    def updateText(self, text):
        self.originalText = text
        self.updateButtonText()
        self.app.saveData() 

    def updateButtonText(self):
        fontMetrics = QFontMetrics(self.textButton.font())
        if self.title:
            buttonText = self.title
        else:
            buttonText = self.originalText
        buttonWidth = self.textButton.width() - 20
        wrappedText = fontMetrics.elidedText(buttonText, Qt.ElideRight, buttonWidth - 20, Qt.TextWrapAnywhere)
        lines = wrappedText.split('\n')
        if len(lines) > 3:
            elidedText = '\n'.join(lines[:3]) + '...'
        else:
            elidedText = wrappedText
        self.textButton.setText(elidedText)
        self.textButton.setToolTip(buttonText)

    def copyText(self, text):
        QApplication.clipboard().setText(self.originalText)
        self.app.copyTextToClipboard(self.originalText)

    def toggleExpand(self):
        if self.expander and self.expander.isVisible():
            self.expander.close()
            self.expander = None
            self.expandButton.setText('▶')
        else:
            if self.app.activeExpander:
                self.app.activeExpander.close()
            # TextExpander 생성 시 parent 매개변수로 self.app을 전달하여 메인 윈도우와 연결
            self.expander = TextExpander(self.originalText, self, parent=self.app)
            self.expander.adjustPosition(self.app)
            self.expander.show()
            self.expandButton.setText('▼')
            self.app.activeExpander = self.expander

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateButtonText()