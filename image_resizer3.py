from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QListWidget, QFileDialog,
                              QMessageBox, QVBoxLayout, QWidget, QProgressBar, QLabel, QComboBox,
                                QLineEdit, QHBoxLayout, QStatusBar, QButtonGroup, QRadioButton)
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
import sys
import os
import threading
from PIL import Image, ImageSequence, ImageOps

# Windows 작업 표시줄 지원
try:
    from PyQt5.QtWinExtras import QWinTaskbarButton, QWinTaskbarProgress
except ImportError:
    QWinTaskbarButton = None  # Windows가 아닌 경우 None으로 설정


class DropArea(QWidget):
    def __init__(self, parent=None):
        super(DropArea, self).__init__(parent)
        self.setAcceptDrops(True)
        self.layout = QVBoxLayout(self)
        self.label = QLabel("↓ Drag and Drop Files Here ↓", self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setFont(QFont('Arial', 14))
        self.label.setStyleSheet("color: #aaa;")
        self.layout.addWidget(self.label)
        self.fileList = QListWidget(self)
        self.fileList.setFont(QFont('Arial', 12))
        self.layout.addWidget(self.fileList)
        self.setStyleSheet("""
            DropArea {
                border: 2px dashed #ccc;
                border-radius: 10px;
                background-color: #fafafa;
            }
            QListWidget {
                border: none;
            }
        """)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.fileList.clear()  # Clear the existing list before adding new files
        for url in event.mimeData().urls():
            if url.isLocalFile():
                self.fileList.addItem(url.toLocalFile())
        self.label.hide()

class ImageResizer(QMainWindow):
    updateProgress = QtCore.pyqtSignal(int)
    showCompleteMessage = QtCore.pyqtSignal()

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.resizeThread = None
        self.updateProgress.connect(self.updateProgressBar)
        self.showCompleteMessage.connect(self.showCompletionMessage)

    def initUI(self):
        self.setWindowTitle('Image Resizer')
        self.setGeometry(100, 100, 800, 600)
        self.center()
        self.setWindowIcon(QIcon(self.resource_path("image_resizer_icon.png")))

        font = QFont()
        font.setPointSize(12)
        QApplication.setFont(font)

        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout(centralWidget)

        self.keepExifCheckbox = QCheckBox("Keep EXIF Data")
        layout.addWidget(self.keepExifCheckbox)

        self.dropArea = DropArea()
        layout.addWidget(self.dropArea)
        layout.setStretchFactor(self.dropArea, 3)  # 드래그 앤 드롭 영역의 비중을 늘립니다.

        self.openButton = QPushButton('Open Files')
        self.openButton.clicked.connect(self.openImages)
        layout.addWidget(self.openButton)

        # Resolution options using radio buttons
        self.resolutionLayout = QHBoxLayout()
        self.resolutionGroup = QButtonGroup(self)
        for ratio in ["1:1", "4:3", "16:9"]:
            radioButton = QRadioButton(ratio)
            self.resolutionGroup.addButton(radioButton)
            self.resolutionLayout.addWidget(radioButton)
            if ratio == "16:9":
                radioButton.setChecked(True)  # Default selection

        # Custom resolution option
        self.customRadioButton = QRadioButton("Custom")  # self 추가
        self.resolutionGroup.addButton(self.customRadioButton)
        self.resolutionLayout.addWidget(self.customRadioButton)
        layout.addLayout(self.resolutionLayout)

        self.customRadioButton.toggled.connect(self.customRatioToggled)  # 여기에 연결

        # Custom resolution inputs
        self.customResolutionWidget = QWidget()  # 이 위젯을 통해 커스텀 입력 필드를 보여주거나 숨깁니다.
        self.customResolutionLayout = QHBoxLayout(self.customResolutionWidget)
        self.widthInput = QLineEdit()
        self.heightInput = QLineEdit()
        self.customResolutionLayout.addWidget(QLabel("Width:"))
        self.customResolutionLayout.addWidget(self.widthInput)
        self.customResolutionLayout.addWidget(QLabel("Height:"))
        self.customResolutionLayout.addWidget(self.heightInput)
        layout.addWidget(self.customResolutionWidget)
        self.customResolutionWidget.setVisible(False)  # 초기 상태에서 숨김


        self.resizeButton = QPushButton('Resize Images')
        self.resizeButton.clicked.connect(self.resizeImages)
        layout.addWidget(self.resizeButton)

        self.progressBar = QProgressBar()
        layout.addWidget(self.progressBar)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.setStyle()

    def setStyle(self):
        self.setStyleSheet("""
            QPushButton {
                background-color: #007AFF; color: white; border-radius: 5px; padding: 10px;
            }
            QPushButton:hover {
                background-color: #357ae8;
            }
            QLineEdit {
                font-size: 14px; padding: 5px; border: 1px solid #cccccc; border-radius: 5px;
            }
            QProgressBar {
                font-size: 14px; padding: 5px; border-radius: 5px; background-color: #f0f0f0; border: 1px solid #cccccc;
            }
            QProgressBar::chunk {
                background-color: #4285f4; border-radius: 5px;
            }
        """)


    def showEvent(self, event):
        super().showEvent(event)
        # Windows 작업 표시줄 진행 상태 표시
        if QWinTaskbarButton:
            self.taskbarButton = QWinTaskbarButton(self)
            self.taskbarButton.setWindow(self.windowHandle())
            self.taskbarProgress = self.taskbarButton.progress()
            self.taskbarProgress.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def openImages(self):
        self.dropArea.fileList.clear()
        filePaths, _ = QFileDialog.getOpenFileNames(self, "Open Images", "", "Image files (*.jpg *.jpeg *.png)")
        for filePath in filePaths:
            self.dropArea.fileList.addItem(filePath)
        if len(filePaths) > 0:
            self.dropArea.label.hide()

    def ratioChanged(self, index):
        if self.ratioComboBox.currentText() == "Custom":
            self.customRatioWidget.show()
        else:
            self.customRatioWidget.hide()

    def resizeImages(self):
        if not self.dropArea.fileList.count():
            QMessageBox.warning(self, 'Warning', 'No images to resize.')
            return

        ratio = self.getRatio()
        if ratio is None:
            QMessageBox.warning(self, 'Error', 'Invalid custom ratio.')
            return

        if not self.resizeThread or not self.resizeThread.is_alive():
            self.resizeThread = threading.Thread(target=self.performResizing, args=(ratio,))
            self.resizeThread.start()

    def customRatioToggled(self, checked):
        self.customResolutionWidget.setVisible(checked)  # 커스텀 비율 입력 위젯의 가시성을 변경

    def getRatio(self):
        if self.customRadioButton.isChecked():  # 여기를 수정
            try:
                width = int(self.widthInput.text())
                height = int(self.heightInput.text())
                if width <= 0 or height <= 0:
                    return None
                return width, height
            except ValueError:
                return None
        else:
            selectedButton = self.resolutionGroup.checkedButton()
            if selectedButton:
                ratioText = selectedButton.text()
                width, height = map(int, ratioText.split(':'))
                return width, height

    def performResizing(self, ratio):
        total_files = self.dropArea.fileList.count()
        for index in range(total_files):
            filePath = self.dropArea.fileList.item(index).text()
            if not self.resizeImage(filePath, ratio):
                self.statusBar().showMessage("Image size too small for selected ratio.", 5000)
                continue
            progress = int((index + 1) / total_files * 100)
            self.updateProgress.emit(progress)
        self.showCompleteMessage.emit()

    def resizeImage(self, filePath, ratio):
            try:
                img = Image.open(filePath)
                if img.format == 'GIF':
                    # Process GIF images
                    frames = []
                    durations = []
                    for frame in ImageSequence.Iterator(img):
                        frame = frame.convert("RGBA")
                        new_frame, duration = self.resizeGIFFrame(frame, ratio)
                        frames.append(new_frame)
                        durations.append(duration)

                    base, ext = os.path.splitext(filePath)
                    resized_file_path = f"{base}_resized.gif" 
                    frames[0].save(resized_file_path, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=False)
                else:
                    # Process non-GIF images
                    new_width, new_height = self.calculateNewSize(img.width, img.height, ratio)
                    resized_img = ImageOps.fit(img, (new_width, new_height), Image.Resampling.LANCZOS)
                    base, ext = os.path.splitext(filePath)
                    resized_file_path = f"{base}_resized{ext}"
                    resized_img.save(resized_file_path)
                return True
            except Exception as e:
                print(f"Error resizing image: {e}")
                return False

    def resizeGIFFrame(self, frame, ratio):
        new_width, new_height = self.calculateNewSize(frame.width, frame.height, ratio)
        frame = ImageOps.fit(frame, (new_width, new_height), Image.Resampling.LANCZOS)
        duration = frame.info.get('duration', 0)  # Preserve frame duration
        return frame, duration


    def calculateNewSize(self, width, height, ratio):
        target_width, target_height = ratio
        aspect_ratio = width / height
        target_aspect_ratio = target_width / target_height

        if aspect_ratio > target_aspect_ratio:
            # 원본이 더 넓은 경우
            new_width = int(height * target_aspect_ratio)
            new_height = height
        else:
            # 원본이 더 높은 경우
            new_width = width
            new_height = int(width / target_aspect_ratio)

        return new_width, new_height

    @QtCore.pyqtSlot(int)
    def updateProgressBar(self, value):
        self.progressBar.setValue(value)
        if self.taskbarProgress:
            self.taskbarProgress.setValue(value)
            if value == 100:
                self.taskbarProgress.hide()

    @QtCore.pyqtSlot()
    def showCompletionMessage(self):
        self.statusBar.showMessage('All images have been resized and saved.', 5000)
        if QWinTaskbarButton:
            self.taskbarProgress.hide()

def main():
    app = QApplication(sys.argv)
    ex = ImageResizer()
    ex.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
