import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QLabel, QComboBox, QRadioButton, QButtonGroup,
    QTextEdit, QPushButton, QFileDialog,
    QCheckBox, QTableView, QGroupBox,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QStatusBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Universal Coordinate Transformer")
        self.resize(500, 700)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        # ==================================================
        # Source CRS
        # ==================================================
        src_group = QGroupBox("Source Coordinate System")
        src_layout = QHBoxLayout(src_group)

        self.src_crs = QComboBox()
        self.src_crs.addItems(["MUTM81", "MUTM84", "MUTM87", "WGS84", "UTM44", "UTM45"])
        src_layout.addWidget(QLabel("CRS:"))
        src_layout.addWidget(self.src_crs)
        src_layout.addStretch()

        main_layout.addWidget(src_group)

        # ==================================================
        # Input Type
        # ==================================================
        input_group = QGroupBox("Input Type")
        input_layout = QHBoxLayout(input_group)

        self.manual_radio = QRadioButton("Manual Input")
        self.file_radio = QRadioButton("File Input")
        self.manual_radio.setChecked(True)

        self.input_mode = QButtonGroup()
        self.input_mode.addButton(self.manual_radio)
        self.input_mode.addButton(self.file_radio)

        input_layout.addWidget(self.manual_radio)
        input_layout.addWidget(self.file_radio)
        input_layout.addStretch()

        main_layout.addWidget(input_group)

        # ==================================================
        # Manual Input
        # ==================================================
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            "Point   X   Y\n"
            "P1   634413.7394   3064905.402\n"
            "P2   634027.2585   3065117.858"
        )

        main_layout.addWidget(self.text_input, stretch=2)

        # ==================================================
        # Output Options
        # ==================================================
        out_group = QGroupBox("Output Coordinate Systems")
        out_layout = QGridLayout(out_group)

        self.chk_wgs = QCheckBox("WGS84")
        self.chk_utm = QCheckBox("UTM")
        self.chk_mutm = QCheckBox("MUTM")

        self.chk_wgs.setChecked(True)
        self.chk_utm.setChecked(True)
        self.chk_mutm.setChecked(True)

        out_layout.addWidget(self.chk_wgs, 0, 0)
        out_layout.addWidget(self.chk_utm, 0, 1)
        out_layout.addWidget(self.chk_mutm, 0, 2)

        main_layout.addWidget(out_group)

        # ==================================================
        # Transform Button
        # ==================================================
        self.transform_btn = QPushButton("Transform Coordinates")
        self.transform_btn.setFixedHeight(40)
        main_layout.addWidget(self.transform_btn)

        # ==================================================
        # Results Table (Preview)
        # ==================================================
        table_group = QGroupBox("Preview Results")
        table_layout = QVBoxLayout(table_group)

        self.table = QTableView()
        self._populate_dummy_table()

        table_layout.addWidget(self.table)
        main_layout.addWidget(table_group, stretch=3)

        # ==================================================
        # Status Bar
        # ==================================================
        status = QStatusBar()
        status.showMessage("Ready | Detected order: EN | Datum: Molodensky (3-param)")
        self.setStatusBar(status)

    def _populate_dummy_table(self):
        """UI demo only"""
        model = QStandardItemModel(3, 6)
        model.setHorizontalHeaderLabels([
            "Point", "Lat", "Lon", "UTM_E", "UTM_N", "Zone"
        ])

        sample = [
            ["P1", "27.69600252", "85.36059200", "338346.5574", "3064602.8440", "45N"],
            ["P2", "27.69795784", "85.35669800", "338012.9911", "3064819.6631", "45N"],
            ["P3", "27.69877247", "85.36371120", "338678.4412", "3064901.2190", "45N"],
        ]

        for r, row in enumerate(sample):
            for c, val in enumerate(row):
                model.setItem(r, c, QStandardItem(val))

        self.table.setModel(model)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.resizeColumnsToContents()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
