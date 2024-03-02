import sys
from PyQt5.QtWidgets import QApplication
from copytxt import Copytxt

def main():
    app = QApplication(sys.argv)
    ex = Copytxt()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
