import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QFrame
)
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer, QDateTime, pyqtSignal
from ProductUser import ProductManager

class NewBatchForm(QWidget):
    logout_signal = pyqtSignal()

    def __init__(self, username=None):
        super().__init__()
        self.username = username
        self.setWindowTitle("Ambu - New Batch Registration")
        self.resize(1900, 1000)
        self.setMinimumSize(1000, 600)
        self.setWindowIcon(QIcon("images/ambu_icon.png"))
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Title Bar
        title_bar = QWidget()
        title_bar.setFixedHeight(80)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)

        # Logo
        logo_label = QLabel()
        logo_label.setPixmap(QPixmap("images/ambu_logo.png").scaled(250, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setFixedSize(250, 70)
        title_layout.addWidget(logo_label)

        # Title
        title_text = QLabel("NEW BATCH REGISTRATION")
        title_text.setFont(QFont("Gabriola", 25, QFont.Bold))
        title_text.setStyleSheet("color: black;")
        title_text.setAlignment(Qt.AlignCenter)
        title_layout.addStretch()
        title_layout.addWidget(title_text)
        title_layout.addStretch()

        # Spacer buttons (Right side)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        # Spacer button
        spacer1 = QPushButton("")
        spacer1.setFixedSize(120, 50)
        spacer1.setCursor(Qt.PointingHandCursor)
        spacer1.setStyleSheet("""
                    QPushButton {
                        padding: 5px 15px;
                        background-color: transparent;
                        border: none;
                    }
                """)

        # Logout Button
        self.logout_btn = QPushButton("LOGOUT")
        self.logout_btn.setFixedSize(120, 50)
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.setStyleSheet("""
                    QPushButton {
                        padding: 5px 15px;
                        background-color: #f5f5f5;
                        color: black;
                        border-radius: 20px;
                        font-size: 18px;
                        border: 1px solid black;
                        font-weight: bold;
                        font-family: Gabriola;
                    }
                    QPushButton:hover {
                        background-color: #da0041;
                        color: white;
                    }
                """)
        self.logout_btn.clicked.connect(self.confirm_logout)

        buttons_layout.addWidget(spacer1)
        buttons_layout.addWidget(self.logout_btn)
        title_layout.addLayout(buttons_layout)
        main_layout.addWidget(title_bar)

        # 2. Clock Bar
        self.lbl_clock = QLabel()
        self.lbl_clock.setFixedHeight(30)
        self.lbl_clock.setFont(QFont("Times New Roman", 12))
        self.lbl_clock.setStyleSheet("background-color: #b60338; color: black;")
        self.lbl_clock.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.lbl_clock)

        # Product Manager Content (integrated between the bars)
        self.product_manager = ProductManager(self.username)
        self.product_manager.setParent(self)
        self.product_manager.setWindowFlags(Qt.Widget)

        # Remove margins from the product manager
        central_widget = self.product_manager.centralWidget()
        if central_widget and central_widget.layout():
            central_widget.layout().setContentsMargins(10, 10, 10, 10)

        main_layout.addWidget(central_widget, 1)  # Takes remaining space

        # Timer setup
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()

        # Footer
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

    def confirm_logout(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Logout")
        msg_box.setText("Are you sure you want to logout?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        reply = msg_box.exec_()
        if reply == QMessageBox.Yes:
            self.logout_signal.emit()
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NewBatchForm()
    window.showFullScreen()
    sys.exit(app.exec_())
