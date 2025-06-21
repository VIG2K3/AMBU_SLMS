import sys
import sqlite3
import hashlib
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox,
    QCheckBox, QVBoxLayout, QSpacerItem, QSizePolicy, QFrame, QGraphicsBlurEffect
)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPainter
from PyQt5.QtCore import Qt

from AdminDash import Dashboard  # Import dashboard

# Database setup
conn = sqlite3.connect('employees.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )
''')
conn.commit()

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ambu - SLMS")
        self.resize(1900, 1000)
        self.setMinimumSize(1000, 600)
        self.setWindowIcon(QIcon("images/ambu_icon.png"))
        self.background = QPixmap("images/bg.jpg")
        self.init_ui()

    def init_ui(self):
        # Logo
        self.logo_label = QLabel(self)
        logo_pixmap = QPixmap("images/ambu_logo.png").scaled(270, 270, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(logo_pixmap)
        self.logo_label.move(40, 20)

        # Blurred background
        self.blur_background = QFrame(self)
        self.blur_background.setStyleSheet("""
            background-color: rgba(180, 180, 180, 0.30);
            border: 1px solid rgba(180, 180, 180, 0.3);
        """)
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(10)
        self.blur_background.setGraphicsEffect(blur)

        # Login panel
        self.login_panel = QFrame(self)
        self.login_panel.setFixedSize(400, 600)
        self.login_panel.setStyleSheet("background: transparent;")
        panel_layout = QVBoxLayout(self.login_panel)
        panel_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        panel_layout.setContentsMargins(30, 30, 30, 30)

        # Profile icon
        self.profile_icon = QLabel()
        pixmap = QPixmap("images/profile_icon.png").scaled(100, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.profile_icon.setPixmap(pixmap)
        self.profile_icon.setAlignment(Qt.AlignCenter)
        self.profile_icon.setStyleSheet("background: transparent; border: none;")
        panel_layout.addWidget(self.profile_icon)

        # Title
        self.title = QLabel("ADMIN LOGIN")
        self.title.setFont(QFont("Gabriola", 35))
        self.title.setStyleSheet("background: transparent; border: none;")
        self.title.setAlignment(Qt.AlignCenter)
        panel_layout.addWidget(self.title)

        panel_layout.addSpacerItem(QSpacerItem(0, 70, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Username
        self.username = QLineEdit("Username")
        self.username.setFont(QFont("Segoe UI", 17))
        self.username.setStyleSheet("""
            QLineEdit {
                background: transparent;
                color: black;
                padding: 8px;
                border: none;
                border-bottom: 3px solid #b60338;
            }
        """)
        self.username.installEventFilter(self)
        panel_layout.addWidget(self.username)

        # Password
        self.password = QLineEdit("Password")
        self.password.setFont(QFont("Segoe UI", 17))
        self.password.setStyleSheet("""
            QLineEdit {
                background: transparent;
                color: black;
                padding: 8px;
                border: none;
                border-bottom: 3px solid #b60338;
            }
        """)
        self.password.setEchoMode(QLineEdit.Normal)
        self.password.installEventFilter(self)
        panel_layout.addWidget(self.password)

        # Show password
        self.show_password = QCheckBox("Show Password")
        self.show_password.setFont(QFont("Segoe UI", 15))
        self.show_password.setStyleSheet("QCheckBox { background: transparent; border: none;}")
        self.show_password.stateChanged.connect(self.toggle_password)
        panel_layout.addWidget(self.show_password)

        panel_layout.addSpacerItem(QSpacerItem(0, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Login button
        self.login_btn = QPushButton("LOGIN")
        self.login_btn.setFont(QFont("Gabriola"))
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
                background-color: #da0041;
            }
        """)
        self.login_btn.clicked.connect(self.login_user)
        panel_layout.addWidget(self.login_btn)

    def resizeEvent(self, event):
        panel_width = self.width() // 2
        self.blur_background.setGeometry(self.width() - panel_width, 0, panel_width, self.height())
        panel_x = self.width() - panel_width + (panel_width - self.login_panel.width()) // 2
        panel_y = (self.height() - self.login_panel.height()) // 2
        self.login_panel.move(panel_x, panel_y)
        super().resizeEvent(event)

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

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def login_user(self):
        username = self.username.text().strip()
        password = self.password.text().strip()

        if username in ["", "Username"] or password in ["", "Password"]:
            QMessageBox.warning(self, "Input Error", "Please enter valid credentials.")
            return

        hashed = self.hash_password(password)

        # Connect to database and check credentials with role
        conn = sqlite3.connect("employees.db")
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM employees WHERE username = ? AND password = ?", (username, hashed))
        result = cursor.fetchone()
        conn.close()

        if result:
            role = result[0]
            if role != "Admin":
                QMessageBox.critical(self, "Access Denied", "Only Admins can access this login.")
                return
            self.open_dashboard()  # Login success
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid username or password.")

    def open_dashboard(self):
        self.dashboard = Dashboard()
        self.dashboard.logout_signal.connect(self.show_login_again)  # Reopen login on logout
        self.dashboard.showFullScreen()
        self.hide()  # Hide login not close

    def show_login_again(self):
        self.username.setText("Username")
        self.password.setText("Password")
        self.password.setEchoMode(QLineEdit.Normal)
        self.show_password.setChecked(False)
        self.showFullScreen()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.showFullScreen()
    sys.exit(app.exec_())
