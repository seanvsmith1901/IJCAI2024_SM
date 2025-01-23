import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QTableWidget, QHBoxLayout, \
    QApplication, QPushButton, QSizePolicy

from RoundState import RoundState
from PyqtLayouts.JhgPanel import JhgPanel
from PyqtLayouts.BodyLayout import BodyLayout


class MainWindow(QMainWindow):
    def __init__(self):
        round_state = RoundState()
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
        body_layout = BodyLayout(round_state)

        # Footer/submit
        foot_layout = QHBoxLayout()
        # submitButton = QPushButton("Submit")
        # foot_layout.addWidget(submitButton)

        # Add the other layouts to the master layout
        master_layout = QVBoxLayout()
        master_layout.addLayout(headerLayout)
        master_layout.addLayout(body_layout)
        master_layout.addLayout(foot_layout)

        central_widget = QWidget()
        central_widget.setLayout(master_layout)

        self.setCentralWidget(central_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()