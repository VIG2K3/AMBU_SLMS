import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QFont, QColor, QIcon
from PyQt5.QtCore import QSize, Qt

class Card(QFrame):
    def __init__(self, title, value):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                padding: 15px;
                border: 1px solid #ddd;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(4, 4)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout()
        titleLabel = QLabel(title)
        titleLabel.setFont(QFont("Segoe UI", 10))
        valueLabel = QLabel(str(value))
        valueLabel.setFont(QFont("Segoe UI", 24, QFont.Bold))

        layout.addWidget(titleLabel)
        layout.addWidget(valueLabel)
        self.setLayout(layout)

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Cards row
        cardsLayout = QHBoxLayout()
        cardsLayout.addWidget(Card("Total Batches", 25))
        cardsLayout.addWidget(Card("Pending Items", 12))
        cardsLayout.addWidget(Card("Active Users", 8))

        layout.addLayout(cardsLayout)
        layout.addStretch()
        self.setLayout(layout)

class PlaceholderPage(QWidget):
    def __init__(self, text):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel(text)
        label.setFont(QFont("Segoe UI", 20))
        layout.addWidget(label, alignment=Qt.AlignCenter)
        self.setLayout(layout)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ambu - Shelf Life Dashboard")
        self.setGeometry(100, 100, 1366, 768)

        # Sidebar buttons
        self.sidebar = QVBoxLayout()
        self.sidebar.setSpacing(20)
        buttons = [
            ("Dashboard", self.show_dashboard),
            ("Batch Details", self.show_batch),
            ("Maturity Status", self.show_maturity),
            ("Employees", self.show_employees),
            ("Reports", self.show_reports),
        ]

        for name, method in buttons:
            btn = QPushButton(name)
            btn.setFont(QFont("Segoe UI", 12))
            btn.setIconSize(QSize(24, 24))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    border-radius: 10px;
                    padding: 10px 20px;
                    border: 1px solid #ddd;
                }
                QPushButton:hover {
                    background-color: #f5f5f5;
                }
            """)
            btn.clicked.connect(method)
            self.sidebar.addWidget(btn)

        self.sidebar.addStretch()

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(self.sidebar)
        sidebar_widget.setFixedWidth(200)

        # Stack for main content
        self.stack = QStackedWidget()
        self.dashboard_page = DashboardPage()
        self.batch_page = PlaceholderPage("Batch Details")
        self.maturity_page = PlaceholderPage("Maturity Status")
        self.employee_page = PlaceholderPage("Employees")
        self.reports_page = PlaceholderPage("Reports")

        for page in [
            self.dashboard_page, self.batch_page, self.maturity_page,
            self.employee_page, self.reports_page
        ]:
            self.stack.addWidget(page)

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(self.stack)

        self.setLayout(main_layout)
        self.show_dashboard()

    def show_dashboard(self):
        self.stack.setCurrentWidget(self.dashboard_page)

    def show_batch(self):
        self.stack.setCurrentWidget(self.batch_page)

    def show_maturity(self):
        self.stack.setCurrentWidget(self.maturity_page)

    def show_employees(self):
        self.stack.setCurrentWidget(self.employee_page)

    def show_reports(self):
        self.stack.setCurrentWidget(self.reports_page)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("QWidget { background-color: #f0f2f5; }")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
