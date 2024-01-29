import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QPushButton, QWidget, QLabel
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon

from fimenaming import FileUploader
from image_resizer2 import ImageResizer
from Move_the_File import MovetheFile

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Utilities")
        self.setWindowIcon(QIcon(self.resource_path("image_resizer_icon.png")))  
        self.resize(800, 600)
        self.initStartScreen()

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def initStartScreen(self):
        self.startWidget = QWidget()
        self.setCentralWidget(self.startWidget)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)
        titleLabel = QLabel("Choose a Utility")
        titleLabel.setAlignment(Qt.AlignCenter)
        titleLabel.setFont(QFont("Arial", 28, QFont.Bold))
        layout.addWidget(titleLabel)

        self.fileRenamerButton = self.createButton("File Renamer", self.resource_path("file_renamer_icon.png"))
        self.fileRenamerButton.clicked.connect(lambda: self.openTab(0))
        layout.addWidget(self.fileRenamerButton)

        self.imageResizerButton = self.createButton("Image Resizer", self.resource_path("image_resizer_icon.png"))
        self.imageResizerButton.clicked.connect(lambda: self.openTab(1))
        layout.addWidget(self.imageResizerButton)

        self.moveFileButton = self.createButton("Move the File", self.resource_path("move_the_file_icon.png")) 
        self.moveFileButton.clicked.connect(lambda: self.openTab(2))
        layout.addWidget(self.moveFileButton)

        self.startWidget.setLayout(layout)

    def createButton(self, text, icon_path):
        button = QPushButton(text)
        button.setFont(QFont("Arial", 18))
        button.setIcon(QIcon(icon_path))
        iconSize = QSize(180, 180)  # 아이콘의 가로와 세로 크기를 40px로 설정
        button.setIconSize(iconSize)  # 설정한 아이콘 크기를 적용
        button.setFixedHeight(70)  # 버튼 세로 크기 조정
        button.setStyleSheet("QPushButton { border: 3px solid #000; border-radius: 15px; padding: 10px; }"
                             "QPushButton:hover { background-color: #e6e6e6; }")
        return button

    def initTabWidget(self):
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("QTabBar::tab { height: 50px; }")
        self.setCentralWidget(self.tab_widget)

        self.tab_widget.addTab(FileUploader(), QIcon(self.resource_path("file_renamer_icon.png")), "File Renamer")
        self.tab_widget.addTab(ImageResizer(), QIcon(self.resource_path("image_resizer_icon.png")), "Image Resizer")
        self.tab_widget.addTab(MovetheFile(), QIcon(self.resource_path("move_the_file_icon.png")), "Move the File") 

    def openTab(self, index):
        self.initTabWidget()
        self.tab_widget.setCurrentIndex(index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())
