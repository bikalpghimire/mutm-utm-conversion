from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Universal Coordinate Transformer")
        self.resize(1200, 800)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
