from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton


class BodyLayout(QHBoxLayout):
    def __init__(self):
        super().__init__()

        playerIdColumn = QVBoxLayout()
        playerIdColumn.addWidget(QLabel("Player"))
        for i in range(0, 11):
            playerIdColumn.addWidget(QLabel("Player " + str(i)))

        popularityColumn = QVBoxLayout()
        popularityColumn.addWidget(QLabel("Popularity"))
        for i in range(0, 11):
            popularityColumn.addWidget(QLineEdit("70"))

        sentColumn = QVBoxLayout()
        sentColumn.addWidget(QLabel("Sent"))
        for i in range(0, 11):
            sentColumn.addWidget(QLineEdit("0"))

        receivedColumn = QVBoxLayout()
        receivedColumn.addWidget(QLabel("Received"))
        for i in range(0, 11):
            receivedColumn.addWidget(QLineEdit("0"))

        allocationsColumn = QVBoxLayout()
        allocationsColumn.addWidget(QLabel("Allocations"))
        for i in range(0, 11):
            allocations_row = QHBoxLayout()

            minus_button = QPushButton("-")
            plus_button = QPushButton("+")

            # Set size policy for buttons to only size to content
            minus_button.setFixedWidth(minus_button.fontMetrics().horizontalAdvance("-") + 20)
            plus_button.setFixedWidth(plus_button.fontMetrics().horizontalAdvance("+") + 20)

            allocation_box = QLineEdit("11")
            allocation_box.setFixedWidth(30)

            allocations_row.addWidget(minus_button)
            allocations_row.addWidget(allocation_box)
            allocations_row.addWidget(plus_button)

            allocationsColumn.addLayout(allocations_row)

        self.addLayout(playerIdColumn)
        self.addLayout(popularityColumn)
        self.addLayout(sentColumn)
        self.addLayout(receivedColumn)
        self.addLayout(allocationsColumn)