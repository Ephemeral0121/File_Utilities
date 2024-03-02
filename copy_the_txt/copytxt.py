import json
import uuid
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton,
                             QTextEdit, QLabel, QScrollArea)
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QFontMetrics, QFont

from .text_button import TextButton
from .text_expander import TextExpander

class Copytxt(QWidget):
    def __init__(self):
        super().__init__()
        self.activeExpander = None
        self.initUI()
        self.loadData()

    def initUI(self):
        self.setWindowTitle('Copy the txt')
        self.setGeometry(100, 100, 800, 600)

        font = QFont()
        font.setPointSize(12)
        QApplication.setFont(font)

        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.setStyleSheet("""
            QWidget {
                font-size: 20px;
            }
            QPushButton {
                background-color: #007AFF;
                color: white;
                border-radius: 5px;
                padding: 14px;
                margin: 1px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #005BCB;
            }
            QPushButton#addButton {
                background-color: #4CAF50;
                font-weight: bold;
                text-align: center;
            }
            QPushButton#addButton:hover {
                background-color: #43A047;
            }
            QTextEdit {
                border: 1px solid #007AFF;
                border-radius: 5px;
                padding: 5px;
                margin-bottom: 10px;
            }
            QLabel {
                color: #007AFF;
                margin: 5px;
            }
        """)

        self.textInput = QTextEdit(self)
        self.textInput.setPlaceholderText('Enter text here...')
        font = self.textInput.font()
        fontMetrics = QFontMetrics(font)
        lineHeight = fontMetrics.lineSpacing()
        self.textInput.setFixedHeight(lineHeight * 4 + 10)
        self.mainLayout.addWidget(self.textInput)

        self.addButton = QPushButton('Add', self)
        self.addButton.setObjectName('addButton')
        self.addButton.clicked.connect(self.onAddButtonClicked)
        self.mainLayout.addWidget(self.addButton)

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollWidget = QWidget()
        self.scrollLayout = QVBoxLayout(self.scrollWidget)
        self.scrollLayout.setAlignment(Qt.AlignTop)
        self.scrollLayout.setSpacing(3)
        self.scrollArea.setWidget(self.scrollWidget)
        self.mainLayout.addWidget(self.scrollArea)

        self.scrollWidget.setAcceptDrops(True)

        self.statusLabel = QLabel('', self)
        self.mainLayout.addWidget(self.statusLabel)

        self.installEventFilter(self)

    def getWidgetIndex(self, widget):
        return self.scrollLayout.indexOf(widget)

    def eventFilter(self, source, event):
        if event.type() == QEvent.User + 1:  # 사용자 정의 이벤트를 확인합니다.
            # CustomEvent의 text 속성을 사용하여 copyTextToClipboard 메서드를 호출합니다.
            self.copyTextToClipboard(event.text)
            return True
        return super().eventFilter(source, event)

    def onAddButtonClicked(self):
        text = self.textInput.toPlainText()
        if text:
            self.addTextButton(text)
            self.textInput.clear()

    def addTextButton(self, text, title=None, id=None, shortcut=None):
        button = TextButton(text, self, self.scrollWidget)
        if id is not None:
            button.id = id  # 고유 ID 할당
        else:
            button.id = str(uuid.uuid4())  # 새 위젯의 경우 새로운 고유 ID 생성
        if title:
            button.updateTitle(title)
        if shortcut:
            button.shortcut = shortcut  # 단축키 할당
            button.registerShortcut(shortcut)  # 단축키 등록
        self.scrollLayout.addWidget(button)
        self.saveData()

    def copyTextToClipboard(self, text):
        singleLineText = text.replace('\n', ' ')
        shortenedText = singleLineText if len(singleLineText) <= 20 else singleLineText[:17] + '...'
        QApplication.clipboard().setText(text)
        self.updateStatusLabel(f'"{shortenedText}" copied to clipboard.')
        self.saveData()

    def toggleExpander(self, text, button):
        if button.expander and button.expander.isVisible():
            button.expander.close()
            button.expander = None
            button.expandButton.setText('▶')
        else:
            if self.activeExpander:
                self.activeExpander.close()
            button.expander = TextExpander(text, button)
            button.expander.adjustPosition(self)
            button.expander.show()
            button.expandButton.setText('▼')
            self.activeExpander = button.expander
        self.saveData()

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        # 드래그된 위젯의 ID 추출
        draggedId = event.mimeData().text()
        draggedIndex = self.findIndexById(draggedId)
        
        # 드롭 위치에 있는 위젯의 인덱스 찾기
        dropPosition = event.pos()
        dropWidget = self.scrollArea.widget().childAt(dropPosition)
        dropIndex = self.findIndexByWidget(dropWidget)
        
        # 위젯 순서 변경
        if 0 <= draggedIndex < self.scrollLayout.count() and 0 <= dropIndex < self.scrollLayout.count():
            self.reorderWidgets(draggedIndex, dropIndex)
            event.acceptProposedAction()

    def reorderWidgets(self, sourceIndex, targetIndex):
        # 위젯 재배치
        widgetToMove = self.scrollLayout.takeAt(sourceIndex).widget()
        # 드래그된 위젯을 제거한 후의 인덱스 변경 고려
        if sourceIndex < targetIndex:
            targetIndex -= 1
        self.scrollLayout.insertWidget(targetIndex, widgetToMove)
        # 변경 사항 저장
        self.saveData()


    def findIndexById(self, id):
        for i in range(self.scrollLayout.count()):
            widget = self.scrollLayout.itemAt(i).widget()
            if hasattr(widget, 'id') and widget.id == id:
                return i
        return -1

    def findIndexByWidget(self, widget):
        if widget:
            return self.scrollLayout.indexOf(widget.parentWidget())
        return -1
    
    def findButtonById(self, id):
        """주어진 ID를 가진 TextButton을 찾아 반환"""
        for i in range(self.scrollLayout.count()):
            widget = self.scrollLayout.itemAt(i).widget()
            if hasattr(widget, 'id') and widget.id == id:
                return widget
        return None

    def moveEvent(self, event):
        super().moveEvent(event)
        if self.activeExpander and self.activeExpander.isVisible():
            self.activeExpander.adjustPosition(self)

    def updateStatusLabel(self, message):
        self.statusLabel.setText(message)
    
    def saveData(self):
        data = []
        for i in range(self.scrollLayout.count()):
            widget = self.scrollLayout.itemAt(i).widget()
            if widget and isinstance(widget, TextButton):
                data.append({
                    'id': widget.id,  # 고유 ID도 저장
                    'text': widget.originalText,
                    'title': widget.title,
                    'shortcut': widget.shortcut  # 단축키 정보 저장
                })
        with open('text_data.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)

    def loadData(self):
        try:
            with open('text_data.json', 'r') as infile:
                data = json.load(infile)
                for item in data:
                    # addTextButton 메서드 호출 시 고유 ID도 전달
                    self.addTextButton(item['text'], item.get('title'), item.get('id'), item.get('shortcut'))
        except FileNotFoundError:
            print("Data file not found. Starting with an empty clipboard.")
        except json.JSONDecodeError:
            print("Error decoding JSON from file.")


    def closeEvent(self, event):
        self.saveData()
        for i in range(self.scrollLayout.count()):
            widget = self.scrollLayout.itemAt(i).widget()
            if widget and isinstance(widget, TextButton) and widget.expander:
                widget.expander.close()
        super().closeEvent(event)