from PyQt5.QtWidgets import QDesktopWidget, QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QTextEdit, QLabel, QComboBox, QSizePolicy, QLineEdit, QMessageBox, QPlainTextEdit
from collections import deque
from PyQt5.QtGui import QIcon, QFont
import sys
import os
import shutil
import pickle
import subprocess

class MovetheFile(QWidget):

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        font = QFont()
        font.setPointSize(12)
        QApplication.setFont(font)
        # 소스 및 타겟 폴더를 위한 변수 초기화
        self.source_folder = ''
        self.target_folder = ''

        # 최근 사용된 폴더 목록
        self.recent_folders = self.load_recent_folders()

        # 아이콘 세팅
        self.setWindowIcon(QIcon(self.resource_path("move_the_file_icon.png")))  

        # 사용자 인터페이스 설정
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        # 소스 폴더 선택 버튼
        self.source_button = QPushButton('Select Source Folder', self)
        self.source_button.clicked.connect(self.select_source)
        self.source_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        vbox.addWidget(self.source_button)

        # 소스 폴더 경로를 표시하는 텍스트 필드
        self.source_folder_label = QLineEdit(self)
        self.source_folder_label.setReadOnly(True)
        vbox.addWidget(self.source_folder_label)

        # 최근 사용된 소스 폴더를 위한 콤보 박스
        self.source_recent = QComboBox(self)
        self.source_recent.addItem('Recent Folders')
        self.source_recent.addItems(self.recent_folders)
        self.source_recent.currentIndexChanged.connect(self.select_source_recent)
        self.source_recent.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        vbox.addWidget(self.source_recent)

        # 타겟 폴더 선택 버튼
        self.target_button = QPushButton('Select Target Folder', self)
        self.target_button.clicked.connect(self.select_target)
        self.target_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        vbox.addWidget(self.target_button)

        # 타겟 폴더 경로를 표시하는 텍스트 필드
        self.target_folder_label = QLineEdit(self)
        self.target_folder_label.setReadOnly(True)
        vbox.addWidget(self.target_folder_label)

        # 최근 사용된 타겟 폴더를 위한 콤보 박스
        self.target_recent = QComboBox(self)
        self.target_recent.addItem('Recent Folders')
        self.target_recent.addItems(self.recent_folders)
        self.target_recent.currentIndexChanged.connect(self.select_target_recent)
        self.target_recent.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        vbox.addWidget(self.target_recent)

        # 키워드 입력을 위한 텍스트 필드
        self.keyword_label = QLabel('Keywords (separated by newline):', self)
        vbox.addWidget(self.keyword_label)

        self.keyword_entry = QTextEdit(self)
        self.keyword_entry.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        vbox.addWidget(self.keyword_entry)

        # 파일 이동 또는 복사를 선택하기 위한 콤보 박스
        self.operation = QComboBox(self)
        self.operation.addItem('Move Files')
        self.operation.addItem('Copy Files')
        self.operation.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        vbox.addWidget(self.operation)

        # 파일 처리 시작 버튼
        self.process_button = QPushButton('Process Files', self)
        self.process_button.clicked.connect(self.process_files)
        self.process_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        vbox.addWidget(self.process_button)

        # 처리된 파일 목록을 표시하는 텍스트 필드
        self.log_label = QLabel('Processed Files:', self)
        vbox.addWidget(self.log_label)

        self.log = QPlainTextEdit(self)
        self.log.setReadOnly(True)
        vbox.addWidget(self.log)

        # 타겟 폴더 오픈 버튼
        self.open_target_button = QPushButton('Open Target Folder', self)
        self.open_target_button.clicked.connect(self.open_target_folder)
        self.open_target_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        vbox.addWidget(self.open_target_button)

        self.styleProcessButton(self.process_button)
        self.styleProcessButton(self.open_target_button)  # 스타일 적용  # 스타일 적용
        
        # 윈도우 타이틀 및 크기 설정, 윈도우 표시
        self.setWindowTitle('File Moving Program')
        self.setGeometry(300, 300, 800, 600)
        self.centerWindow()

        self.show()

    def centerWindow(self):
        # 창을 화면의 중앙에 배치하는 메소드
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def load_recent_folders(self):
        # 최근 사용된 폴더 목록을 불러옴
        try:
            with open('recent_folders.pickle', 'rb') as f:
                return pickle.load(f)
        except (FileNotFoundError, EOFError):  # EOFError 처리 추가
            return deque(maxlen=5)

    def save_recent_folders(self):
        # 최근 사용된 폴더 목록을 저장
        with open('recent_folders.pickle', 'wb') as f:
            pickle.dump(self.recent_folders, f)

    def add_recent_folder(self, folder):
        # 폴더를 최근 사용된 폴더 목록에 추가
        if folder in self.recent_folders:
            self.recent_folders.remove(folder)
        self.recent_folders.appendleft(folder)
        self.save_recent_folders()

    def select_source(self):
        # 소스 폴더 선택
        self.source_folder = QFileDialog.getExistingDirectory(self, 'Select Source Folder')
        if self.source_folder:
            self.source_folder_label.setText(self.source_folder)
            self.add_recent_folder(self.source_folder)
            self.source_recent.clear()
            self.source_recent.addItem('Recent Folders')
            self.source_recent.addItems(self.recent_folders)

    def select_source_recent(self, index):
        # 최근 사용된 소스 폴더 선택
        if index > 0:
            self.source_folder = self.recent_folders[index-1]
            self.source_folder_label.setText(self.source_folder)

    def select_target(self):
        # 타겟 폴더 선택
        self.target_folder = QFileDialog.getExistingDirectory(self, 'Select Target Folder')
        if self.target_folder:
            self.target_folder_label.setText(self.target_folder)
            self.add_recent_folder(self.target_folder)
            self.target_recent.clear()
            self.target_recent.addItem('Recent Folders')
            self.target_recent.addItems(self.recent_folders)

    def select_target_recent(self, index):
        # 최근 사용된 타겟 폴더 선택
        if index > 0:
            self.target_folder = self.recent_folders[index-1]
            self.target_folder_label.setText(self.target_folder)

    def process_files(self):
        # 파일 처리
        try:
            keywords = self.keyword_entry.toPlainText().split('\n')
            # 키워드가 입력되지 않은 경우 함수 종료
            if not any(keywords):
                QMessageBox.information(self, "Notice", "Please enter the keywords")
                return
            processed_files = []
            for root, dirs, files in os.walk(self.source_folder):
                for file_name in files:
                    if any(keyword in file_name for keyword in keywords if keyword):
                        source_file = os.path.join(root, file_name)

                        # 원본 폴더 구조에서의 상대 경로 계산
                        relative_path = os.path.relpath(root, self.source_folder)
                        target_dir = os.path.join(self.target_folder, relative_path)

                        # 소스 폴더의 직접적인 하위가 아닌 경우만 중복 검사 수행
                        if relative_path != '.':
                            # 타겟 파일 경로 설정
                            target_file = os.path.join(self.target_folder, file_name)

                            # 파일명 중복 시 처리
                            base, extension = os.path.splitext(file_name)
                            counter = 1
                            while os.path.exists(target_file):
                                target_file = os.path.join(self.target_folder, f"{base}_{counter}{extension}")
                                counter += 1

                            # 파일 이동 또는 복사
                            if self.operation.currentText() == 'Move Files':
                                os.makedirs(target_dir, exist_ok=True)
                                shutil.move(source_file, target_file)
                            elif self.operation.currentText() == 'Copy Files':
                                os.makedirs(target_dir, exist_ok=True)
                                shutil.copy2(source_file, target_file)

                            processed_files.append(os.path.basename(target_file))
                        else:
                            # 소스 폴더에 직접 위치한 파일은 아무런 조치 없이 목록에 추가만 함
                            processed_files.append(file_name)

            if processed_files:
                # 프로세스 파일 표시
                self.log.appendPlainText(f"\n{len(processed_files)} files have been {self.operation.currentText()}:\n" + "\n".join(processed_files))
                QMessageBox.information(self, "Success", f"{len(processed_files)} file processing is complete.")
            else:
                QMessageBox.information(self, "Notification", "There are no files matching the keyword.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def open_target_folder(self):
        if self.target_folder:
            if sys.platform == 'win32':
                os.startfile(self.target_folder)
            elif sys.platform == 'darwin':  # macOS
                subprocess.Popen(['open', self.target_folder])
            else:  # linux variants
                subprocess.Popen(['xdg-open', self.target_folder])
        else:
            QMessageBox.information(self, "Notice", "No target folder selected")

    def styleProcessButton(self, button):
        # 프로세스 버튼 스타일링
        button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF; color: white;
                border-radius: 5px; padding: 10px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MovetheFile()
    sys.exit(app.exec_())
