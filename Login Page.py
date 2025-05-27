import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox,
    QCheckBox, QVBoxLayout, QHBoxLayout, QFrame, QSpacerItem, QSizePolicy,
    QGraphicsBlurEffect
)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPainter
from PyQt5.QtCore import Qt

# Database setup
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )
''')
conn.commit()

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ambu - Shelf Life Management System")
        self.resize(1900, 1000)
        self.setMinimumSize(1000, 600)
        self.setWindowIcon(QIcon("ambu_icon.png"))
        self.background = QPixmap("bg.jpg")
        self.init_ui()

    def init_ui(self):
        # Logo
        self.logo_label = QLabel(self)
        logo_pixmap = QPixmap("ambu_logo.png").scaled(250, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(logo_pixmap)
        self.logo_label.move(40, 20)

        # Blurred Background layout
        self.blur_background = QFrame(self)
        self.blur_background.setStyleSheet("""
            background-color: rgba(180, 180, 180, 0.30);
            border: 1px solid rgba(180, 180, 180, 0.10);
        """)
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(10)
        self.blur_background.setGraphicsEffect(blur)

        # Login Panel layout
        self.login_panel = QFrame(self)
        self.login_panel.setFixedSize(400, 600)
        self.login_panel.setStyleSheet("background: transparent;")

        # Layout inside login panel
        panel_layout = QVBoxLayout(self.login_panel)
        panel_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        panel_layout.setContentsMargins(30, 30, 30, 30)

        # Profile icon
        self.profile_pic = QLabel()
        pixmap = QPixmap("profile_Icon.png").scaled(100, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.profile_pic.setPixmap(pixmap)
        self.profile_pic.setAlignment(Qt.AlignCenter)
        self.profile_pic.setStyleSheet("background: transparent; border: none;")
        panel_layout.addWidget(self.profile_pic)

        # Title
        self.title = QLabel("USER LOGIN")
        self.title.setFont(QFont('Gabriola', 35))
        self.title.setStyleSheet("background: transparent; border: none;")
        self.title.setAlignment(Qt.AlignCenter)
        panel_layout.addWidget(self.title)

        panel_layout.addSpacerItem(QSpacerItem(0, 70, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Username
        self.username = QLineEdit("Username")
        self.username.setFont(QFont('Arial', 14))
        self.username.setStyleSheet("""
            QLineEdit {
                background: transparent;
                color: black;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #b60338;
            }
        """)
        self.username.installEventFilter(self)
        panel_layout.addWidget(self.username)

        # Password
        self.password = QLineEdit("Password")
        self.password.setFont(QFont('Arial', 14))
        self.password.setStyleSheet("""
            QLineEdit {
                background: transparent;
                color: black;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #b60338;
            }
        """)
        self.password.setEchoMode(QLineEdit.Normal)
        self.password.installEventFilter(self)
        panel_layout.addWidget(self.password)

        # Show password
        self.show_password = QCheckBox("Show Password")
        self.show_password.setFont(QFont('Arial', 12))
        self.show_password.setStyleSheet("QCheckBox { background: transparent; border: none; }")
        self.show_password.stateChanged.connect(self.toggle_password)
        panel_layout.addWidget(self.show_password)

        panel_layout.addSpacerItem(QSpacerItem(0, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Login button
        self.login_btn = QPushButton("LOGIN")
        self.login_btn.setFont(QFont('Gabriola'))
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #b60338;
                color: white;
                font-size: 30px;
                font-weight: bold;
                border: none;
                padding: 5px;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #913752;
            }
        """)
        self.login_btn.clicked.connect(self.login_user)
        panel_layout.addWidget(self.login_btn)

        # Blurred background position
    def resizeEvent(self, event):
        panel_width = self.width() // 2
        self.blur_background.setGeometry(self.width() - panel_width, 0, panel_width, self.height())

        # Login panel position
        panel_x = self.width() - panel_width + (panel_width - self.login_panel.width()) // 2
        panel_y = (self.height() - self.login_panel.height()) // 2
        self.login_panel.move(panel_x, panel_y)

        super().resizeEvent(event)

        # Background sizing
    def paintEvent(self, event):
        painter = QPainter(self)
        scaled_bg = self.background.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        painter.drawPixmap(0, 0, scaled_bg)

    def eventFilter(self, source, event):
        if source == self.username:
            if event.type() == event.FocusIn and self.username.text() == "Username":
                self.username.setText("")
            elif event.type() == event.FocusOut and self.username.text() == "":
                self.username.setText("Username")
        elif source == self.password:
            if event.type() == event.FocusIn and self.password.text() == "Password":
                self.password.setText("")
                self.password.setEchoMode(QLineEdit.Password if not self.show_password.isChecked() else QLineEdit.Normal)
            elif event.type() == event.FocusOut and self.password.text() == "":
                self.password.setText("Password")
                self.password.setEchoMode(QLineEdit.Normal)
        return super().eventFilter(source, event)

    def toggle_password(self):
        if self.password.text() != "Password":
            self.password.setEchoMode(QLineEdit.Normal if self.show_password.isChecked() else QLineEdit.Password)

    def login_user(self):
        username = self.username.text()
        password = self.password.text()

        if username in ["", "Username"] or password in ["", "Password"]:
            QMessageBox.warning(self, "Input Error", "Please enter valid credentials.")
            return

        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        result = cursor.fetchone()

        if result:
            QMessageBox.information(self, "Login Successful", f"Welcome, {username}!")
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid username or password.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
