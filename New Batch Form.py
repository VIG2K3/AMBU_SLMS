import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QFrame, QMessageBox
)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor
from PyQt5.QtCore import Qt, QTimer, QDateTime
from ProductUser import ProductManager

class NewBatchForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ambu - Shelf Life Management System")
        self.resize(1900, 1000)
        self.setMinimumSize(1000, 600)
        self.setWindowIcon(QIcon("ambu_icon.png"))
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Title Bar (exact copy from your original)
        title_bar = QWidget()
        title_bar.setFixedHeight(70)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)

        # Logo
        logo_label = QLabel()
        logo_label.setPixmap(QPixmap("ambu_logo.png").scaled(250, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setFixedSize(250, 70)
        title_layout.addWidget(logo_label)

        # Title
        title_text = QLabel("NEW BATCH REGISTRATION FORM")
        title_text.setFont(QFont("Gabriola", 25, QFont.Bold))
        title_text.setStyleSheet("color: black;")
        title_text.setAlignment(Qt.AlignCenter)
        title_layout.addStretch()
        title_layout.addWidget(title_text)
        title_layout.addStretch()

        # Spacer buttons (Right side)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        # Spacer buttons (preserved from your original)
        spacer1 = QPushButton("")
        spacer1.setFixedSize(120, 50)
        spacer1.setCursor(Qt.PointingHandCursor)
        spacer1.setStyleSheet("""QPushButton {padding: 5px 15px; background-color: transparent;}""")
        
        spacer2 = QPushButton("")
        spacer2.setFixedSize(120, 50)
        spacer2.setCursor(Qt.PointingHandCursor)
        spacer2.setStyleSheet("""QPushButton {padding: 5px 15px; background-color: transparent;}""")
        
        buttons_layout.addWidget(spacer1)
        buttons_layout.addWidget(spacer2)
        title_layout.addLayout(buttons_layout)
        main_layout.addWidget(title_bar)

        # 2. Clock Bar (exact copy from your original)
        self.lbl_clock = QLabel()
        self.lbl_clock.setFixedHeight(30)
        self.lbl_clock.setFont(QFont("Times New Roman", 12))
        self.lbl_clock.setStyleSheet("background-color: #b60338; color: black;")
        self.lbl_clock.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.lbl_clock)

        # 3. Product Manager Content (integrated between the bars)
        self.product_manager = ProductManager()
        self.product_manager.setParent(self)
        self.product_manager.setWindowFlags(Qt.Widget)
        
        # Remove margins from the product manager
        central_widget = self.product_manager.centralWidget()
        central_widget.layout().setContentsMargins(10, 10, 10, 10)
        
        main_layout.addWidget(central_widget, 1)  # Takes remaining space

        # Timer setup
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()

    def update_clock(self):
        current_datetime = QDateTime.currentDateTime()
        date_str = current_datetime.toString("dd-MM-yyyy")
        time_str = current_datetime.toString("HH:mm:ss")
        self.lbl_clock.setText(f"Date: {date_str}    Time: {time_str}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NewBatchForm()
    window.showMaximized()
    sys.exit(app.exec_())
