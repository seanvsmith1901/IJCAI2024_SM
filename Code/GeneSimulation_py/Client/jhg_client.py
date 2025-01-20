import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QTableWidget, QHBoxLayout, \
    QApplication, QPushButton, QSizePolicy

from PyqtLayouts.body_layout import BodyLayout


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("JHG")

        # Header
        headerLayout = QHBoxLayout()
        roundCounter = QLabel("Round 1")
        roundCounterFont = QFont()
        roundCounterFont.setPointSize(20)
        roundCounter.setFont(roundCounterFont)
        headerLayout.addWidget(roundCounter)

        # Body
        bodyLayout = BodyLayout()

        # Footer/submit
        footLayout = QHBoxLayout()
        submitButton = QPushButton("Submit")
        footLayout.addWidget(submitButton)

        # Add the other layouts to the master layout
        master_layout = QVBoxLayout()
        master_layout.addLayout(headerLayout)
        master_layout.addLayout(bodyLayout)
        master_layout.addLayout(footLayout)

        central_widget = QWidget()
        central_widget.setLayout(master_layout)

        self.setCentralWidget(central_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()