import sys
import os
import re
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QLabel, QLineEdit, QSpinBox, QListView, QHBoxLayout)
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QFont

def natural_sort_key(s):
    """숫자를 포함한 문자열을 올바르게 정렬."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]


class FileUploader(QMainWindow):
    def __init__(self):
        super(FileUploader, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("File Renamer")
        self.resize(800, 600)
        self.setFont(QFont('Arial', 10))

        layout = QVBoxLayout()

        self.dragDropLabel = QLabel("↓ Drag and Drop Files Here ↓")
        self.dragDropLabel.setAlignment(Qt.AlignCenter)
        self.dragDropLabel.setFont(QFont('Arial', 12, QFont.Bold))
        self.dragDropLabel.setStyleSheet("border: 2px dashed #ccc; color: #888; padding: 10px; margin-top: 20px; margin-bottom: 20px;")
        layout.addWidget(self.dragDropLabel)

        self.file_list = QStringListModel()
        self.file_view = QListView()
        self.file_view.setModel(self.file_list)
        layout.addWidget(self.file_view)

        self.keywordLabel = QLabel("Rename Keyword:")
        self.keywordEdit = QLineEdit()
        self.keywordEdit.setPlaceholderText("ex) img -> img01, img02, img03, ...")  # 플레이스홀더 텍스트 추가
        self.keywordEdit.setStyleSheet("margin-top: 10px; margin-bottom: 10px;")
        self.startNumberLabel = QLabel("Start Number:")
        self.startNumberSpin = QSpinBox()
        self.startNumberSpin.setRange(1, 9999)

        settingsLayout = QHBoxLayout()
        settingsLayout.addWidget(self.keywordLabel)
        settingsLayout.addWidget(self.keywordEdit)
        settingsLayout.addWidget(self.startNumberLabel)
        settingsLayout.addWidget(self.startNumberSpin)
        layout.addLayout(settingsLayout)

        self.renameButton = QPushButton("Rename and Save")
        self.renameButton.setFont(QFont('Arial', 10))
        self.renameButton.setStyleSheet("QPushButton { background-color: #007AFF; color: white; border-radius: 5px; padding: 10px; } QPushButton:hover { background-color: #0056b3; }")
        self.renameButton.clicked.connect(self.renameAndSave)
        layout.addWidget(self.renameButton)

        mainWidget = QWidget()
        mainWidget.setLayout(layout)
        self.setCentralWidget(mainWidget)
        self.setAcceptDrops(True)


    def addFiles(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select files")
        if files:
            current_files = self.file_list.stringList()
            new_files = sorted(set(files).union(current_files), key=natural_sort_key)
            self.file_list.setStringList(new_files)

    def dropEvent(self, event: QDropEvent):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        new_files = sorted(set(files), key=natural_sort_key)
        self.file_list.setStringList(new_files)

    def renameAndSave(self):
        temp_file_list = []
        updated_file_list = []
        rename_keyword = self.keywordEdit.text().strip()
        number = self.startNumberSpin.value()

        for i, file_path in enumerate(self.file_list.stringList(), start=1):
            dir_name, old_file_name = os.path.split(file_path)
            file_extension = os.path.splitext(old_file_name)[1]
            temp_file_name = self.generate_temp_name(i) + file_extension
            temp_path = os.path.join(dir_name, temp_file_name)
            os.rename(file_path, temp_path)
            temp_file_list.append((temp_path, file_extension))

        current_files = set(self.file_list.stringList())  # 현재 리스트에 있는 파일 이름을 집합으로 변환

        for temp_path, file_extension in temp_file_list:
            new_file_name = f"{rename_keyword}{str(number).zfill(2)}{file_extension}"
            new_path = os.path.join(os.path.dirname(temp_path), new_file_name)
            
            # 파일 이름 충돌 방지 로직: 파일 시스템 내에 이름이 존재하고 리스트에는 없을 때
            while os.path.exists(new_path) and new_path not in current_files:
                number += 1
                new_file_name = f"{rename_keyword}{str(number).zfill(2)}{file_extension}"
                new_path = os.path.join(os.path.dirname(temp_path), new_file_name)
            
            os.rename(temp_path, new_path)
            updated_file_list.append(new_path)
            current_files.add(new_path)  # 새 경로를 현재 파일 집합에 추가
            number += 1

        self.file_list.setStringList(sorted(updated_file_list, key=natural_sort_key))


    def generate_temp_name(self, number):
        random_digits = random.randint(1000, 9999)
        return f"A{random_digits}temp{str(number).zfill(2)}"

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = FileUploader()
    win.show()
    sys.exit(app.exec_())
