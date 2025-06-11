import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QFrame, QMessageBox
)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor
from PyQt5.QtCore import Qt, QTimer, QDateTime


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ambu - Shelf Life Management System")
        self.resize(1900, 1000)
        self.setMinimumSize(1000, 600)
        self.setWindowIcon(QIcon("ambu_icon.png"))
        self.setStyleSheet("background-color: #d9d9d9;")
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)

        # Title Bar
        title_bar = QWidget()
        title_bar.setFixedHeight(70)
        self.title_bar = title_bar
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)

        # Logo
        self.logo_label = QLabel()
        self.logo_label.setPixmap(QPixmap("ambu_logo.png").scaled(250, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_label.setFixedSize(250, 70)
        title_layout.addWidget(self.logo_label)

        # Title
        self.title_text = QLabel("NEW BATCH REGISTRATION FORM")
        self.title_text.setFont(QFont("Gabriola", 25, QFont.Bold))
        self.title_text.setStyleSheet("color: black;")
        self.title_text.setAlignment(Qt.AlignCenter)
        title_layout.addStretch()
        title_layout.addWidget(self.title_text)
        title_layout.addStretch()

        # Spacer buttons (Right side)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        # Spacer 1
        self.spacer1 = QPushButton("")
        self.spacer1.setFixedSize(120, 50)
        self.spacer1.setCursor(Qt.PointingHandCursor)
        self.spacer1.setStyleSheet("""
                QPushButton {
                    padding: 5px 15px;
                    background-color: #d9d9d9;
                    border: 1px solid #d9d9d9;
                }
                """)
        buttons_layout.addWidget(self.spacer1)

        # Spacer 2
        self.spacer2 = QPushButton("")
        self.spacer2.setFixedSize(120, 50)
        self.spacer2.setCursor(Qt.PointingHandCursor)
        self.spacer2.setStyleSheet("""
        QPushButton {
            padding: 5px 15px;
            background-color: #d9d9d9;
            border: 1px solid #d9d9d9;
        }
        """)
        buttons_layout.addWidget(self.spacer2)

        title_layout.addLayout(buttons_layout)
        main_layout.addWidget(title_bar)

        # Clock
        self.lbl_clock = QLabel()
        self.lbl_clock.setFixedHeight(30)
        self.lbl_clock.setFont(QFont("Times New Roman", 12))
        self.lbl_clock.setStyleSheet("background-color: #b60338; color: black;")
        self.lbl_clock.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.lbl_clock)

        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)
        self.update_clock()

        # Main Content
        content_layout = QHBoxLayout()
        main_content_layout = QVBoxLayout()
        content_widget = QWidget()
        content_widget.setLayout(main_content_layout)
        content_layout.addWidget(content_widget, 8)
        main_layout.addLayout(content_layout)

        self.footer = QLabel("Copyright ©2025 Ambu A/S")
        self.footer.setFont(QFont("Times New Roman", 12))
        self.footer.setStyleSheet("background-color: #b60338; color: black;")
        self.footer.setAlignment(Qt.AlignCenter)
        self.footer.setFixedHeight(30)
        main_layout.addWidget(self.footer)

    def update_clock(self):
        current_datetime = QDateTime.currentDateTime()
        date_str = current_datetime.toString("dd-MM-yyyy")
        time_str = current_datetime.toString("HH:mm:ss")
        self.lbl_clock.setText(f"Date: {date_str}    Time: {time_str}")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec_())
