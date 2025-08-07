import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread

if __name__ == '__main__':
    app = QApplication(sys.argv)
    thread = QThread()
    print("PyQt5 and QThread imported successfully!")
    sys.exit(0)