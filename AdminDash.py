import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QFrame, QMessageBox
)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor
from PyQt5.QtCore import Qt, QTimer, QDateTime

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ambu - SLMS")
        self.resize(1900, 1000)
        self.setMinimumSize(1000, 600)
        self.setWindowIcon(QIcon("ambu_icon.png"))
        self.setStyleSheet("background-color: #d9d9d9;")
        self.dark_mode = False
        self.sidebar_buttons = []
        self.dynamic_labels = []
        self.tables = []
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
        self.logo_label.setPixmap(QPixmap("ambu_logo.png").scaled(250, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_label.setFixedSize(250, 80)
        title_layout.addWidget(self.logo_label)

        # Title
        self.title_text = QLabel("SHELF LIFE MANAGEMENT SYSTEM")
        self.title_text.setFont(QFont("Gabriola", 25, QFont.Bold))
        self.title_text.setStyleSheet("color: black;")
        self.title_text.setAlignment(Qt.AlignCenter)
        title_layout.addStretch()
        title_layout.addWidget(self.title_text)
        title_layout.addStretch()

        # Right-side buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        # Dark Mode Button
        self.theme_btn = QPushButton("DARK MODE")
        self.theme_btn.setFixedSize(120, 50)
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.setStyleSheet("""
                QPushButton {
                    padding: 5px 15px;
                    background-color: white;
                    color: black;
                    border-radius: 20px;
                    font-size: 18px;
                    border: 1px solid black;
                    font-weight: bold;
                    font-family: Gabriola;
                }
                QPushButton:hover {
                    background-color: #f31659;
                }
                """)
        self.theme_btn.clicked.connect(self.toggle_theme)
        buttons_layout.addWidget(self.theme_btn)

        # Logout Button
        self.logout_btn = QPushButton("LOGOUT")
        self.logout_btn.setFixedSize(120, 50)
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.setStyleSheet("""
        QPushButton {
            padding: 5px 15px;
            background-color: white;
            color: black;
            border-radius: 20px;
            font-size: 18px;
            border: 1px solid black;
            font-weight: bold;
            font-family: Gabriola;
        }
        QPushButton:hover {
            background-color: #f31659;
        }
        """)
        self.logout_btn.clicked.connect(self.confirm_logout)
        buttons_layout.addWidget(self.logout_btn)

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

        content_layout = QHBoxLayout()

        # Sidebar
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setStyleSheet("background-color: #b60338; color: white;")
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setContentsMargins(20, 10, 20, 10)
        sidebar_layout.setSpacing(8)

        menu_label = QLabel("MENU")
        menu_label.setFont(QFont("Gabriola", 30, QFont.Bold))
        menu_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(menu_label)

        options = ["HOMEPAGE", "BATCH DETAILS", "MATURITY STATUS", "EMPLOYEES", "REPORTS"]
        for option in options:
            btn = QPushButton(option)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: center;
                    padding: 2px 30px;
                    color: black;
                    background: white;
                    border: 1px solid black;
                    border-radius: 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #f31659;
                }
            """)
            btn.setFont(QFont("Gabriola", 20))
            btn.setCursor(Qt.PointingHandCursor)
            sidebar_layout.addWidget(btn)
            self.sidebar_buttons.append(btn)

        sidebar_layout.addStretch()
        content_layout.addWidget(self.sidebar_widget, 1)

        # Main Content
        main_content_layout = QVBoxLayout()

        top_bar = QHBoxLayout()
        self.dash_bar = QLineEdit()
        self.dash_bar.setText("DASHBOARD")
        self.dash_bar.setReadOnly(True)
        self.dash_bar.setFixedHeight(30)
        self.dash_bar.setStyleSheet("""
                    padding-left: 10px;
                    border-radius: none;
                    font-size: 35px;
                    color: black;
                    background-color: transparent;
                    font-weight: bold;
                    font-family: Gabriola;
                """)

        self.profile_label = QLabel("")
        self.profile_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Bell Icon
        bell_icon = QLabel()
        pixmap = QPixmap("bell_icon.png").scaled(40, 40, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        bell_icon.setPixmap(pixmap)
        bell_icon.setFixedSize(40, 40)
        bell_icon.setStyleSheet("border-radius: 100px; background-color: transparent;")

        top_bar.addWidget(self.dash_bar, 4)
        top_bar.addStretch()
        top_bar.addWidget(self.profile_label)
        top_bar.addWidget(bell_icon)
        main_content_layout.addLayout(top_bar)

        # Stats boxes
        stats_layout = QHBoxLayout()
        for title in ["Total Batch", "Total User", "Pending Status"]:
            box = QVBoxLayout()
            lbl_title = QLabel(title)
            lbl_count = QLabel("0")
            lbl_title.setStyleSheet("color: black;")
            lbl_count.setStyleSheet("font-size: 25px; font-weight: bold;")
            box.addWidget(lbl_title)
            box.addWidget(lbl_count)
            box_frame = QFrame()
            box_frame.setLayout(box)
            box_frame.setStyleSheet("background-color: white; padding: 5px; border-radius: 10px;")
            stats_layout.addWidget(box_frame)
        main_content_layout.addLayout(stats_layout)

        # Bar Chart
        self.chart_container = QWidget()
        self.chart_container.setFixedHeight(350)
        self.chart_layout = QVBoxLayout(self.chart_container)
        self.chart_layout.setContentsMargins(0, 0, 0, 0)
        self.create_bar_chart()
        main_content_layout.addWidget(self.chart_container)

        # Maturity Table
        self.maturity_table = QTableWidget(10, 5)
        self.maturity_table.setHorizontalHeaderLabels(["BATCH ID", "BATCH NAME", "QUANTITY", "DUE DATE", "STATUS"])
        self.maturity_table.verticalHeader().setVisible(False)
        self.maturity_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.maturity_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.maturity_table.setFixedHeight(250)
        self.maturity_table.setStyleSheet("""
            QTableWidget {
                    background-color: white;
                    color: black;
                    border-radius: 10px;
                }
                QHeaderView::section {
                    background-color: #f0f0f0;
                    color: black;
                    font-size: 23px;
                    font-weight: bold;
                    font-family: Gabriola;
            }
        """)

        sample_data = [
            ("", "", "", "", "Pending"),
            ("", "", "", "", "Pending"),
            ("", "", "", "", "Pending"),
            ("", "", "", "", "Pending"),
            ("", "", "", "", "Pending")
        ]

        for row, (employee, leave_type, date_range, days, status) in enumerate(sample_data):
            self.maturity_table.setItem(row, 0, QTableWidgetItem(employee))
            self.maturity_table.setItem(row, 1, QTableWidgetItem(leave_type))
            self.maturity_table.setItem(row, 2, QTableWidgetItem(date_range))
            self.maturity_table.setItem(row, 3, QTableWidgetItem(days))

            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor("orange"))
            self.maturity_table.setItem(row, 4, status_item)

        self.maturity_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_content_layout.addWidget(self.maturity_table)

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

    def confirm_logout(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Logout")
        msg_box.setText("Are you sure you want to logout?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        if self.dark_mode:
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #121212;
                    color: white;
                    font-size: 16px;
                }
                QLabel {
                    color: white;
                    font-size: 16px;
                }
                QPushButton {
                    background-color: white;
                    color: black;
                }
                QPushButton:hover {
                    background-color: #121212;
                }
            """)
        else:
            msg_box.setStyleSheet("")

        reply = msg_box.exec_()
        if reply == QMessageBox.Yes:
            self.logout_signal.emit()  # ✅ Emit signal
            self.close()  # ✅ Close dashboard

    def toggle_theme(self):
        if self.dark_mode:
            # Light Mode
            self.setStyleSheet("background-color: #d9d9d9;")
            self.profile_label.setStyleSheet("color: black;")
            self.lbl_clock.setStyleSheet("background-color: #b60338; color: black;")
            self.sidebar_widget.setStyleSheet("background-color: #b60338; color: white;")
            self.footer.setStyleSheet("background-color: #b60338; color: black;")
            self.dash_text.setStyleSheet("padding-left: 10px; border-radius: none; font-size: 40px; color: black; background-color: transparent; font-family: Gabriola;")
            self.title_text.setStyleSheet("color: black;")
            self.logout_btn.setStyleSheet("QPushButton {padding: 5px 15px; background-color: white; color: black; border-radius: 15px; font-size: 18px; border: 1px solid black; font-weight: bold; font-family: Gabriola;} QPushButton:hover {background-color: rgba(255, 255, 255, 0.2);}")
            self.theme_btn.setText("DARK MODE")
            self.theme_btn.setStyleSheet("QPushButton {padding: 5px 15px; background-color: white; color: black; border-radius: 15px; font-size: 18px; border: 1px solid black; font-weight: bold; font-family: Gabriola;} QPushButton:hover {background-color: rgba(255, 255, 255, 0.2);}")
            self.trend_label.setStyleSheet("background-color: #d9d9d9; color: black; padding: 20px; border-radius: 10px;")
            self.upcoming_label.setStyleSheet("background-color: #d9d9d9; color: black;")
            self.pending_label.setStyleSheet("background-color: #d9d9d9; color: black;")
            for btn in self.sidebar_buttons:
                btn.setStyleSheet("QPushButton {background: white; color: black; font-weight: bold; border: 1px solid black; border-radius: 15px; text-align: center; padding: 2px 12px; font-family: Gabriola;} QPushButton:hover {background-color: rgba(255, 255, 255, 0.2);}")
            for label in self.dynamic_labels:
                label.setStyleSheet("background-color: white; color: black; padding: 20px; border-radius: 10px;")
            self.dark_mode = False
        else:
            # Dark Mode
            self.setStyleSheet("background-color: #121212;")
            self.profile_label.setStyleSheet("color: white;")
            self.lbl_clock.setStyleSheet("background-color: #333; color: white;")
            self.sidebar_widget.setStyleSheet("background-color: #333; color: white;")
            self.footer.setStyleSheet("background-color: #333; color: white;")
            self.dash_text.setStyleSheet("padding-left: 10px; border-radius: none; font-size: 40px; color: white; background-color: transparent; font-family: Gabriola;")
            self.title_text.setStyleSheet("color: white;")
            self.logout_btn.setStyleSheet("QPushButton {padding: 5px 15px; background-color: white; color: black; border-radius: 15px; font-size: 18px; border: 1px solid black; font-weight: bold; font-family: Gabriola;} QPushButton:hover {background-color: rgba(255, 255, 255, 0.50);}")
            self.theme_btn.setText("LIGHT MODE")
            self.theme_btn.setStyleSheet("QPushButton {padding: 5px 15px; background-color: #333; color: white; border-radius: 15px; font-size: 18px; border: 1px solid black; font-weight: bold; font-family: Gabriola;} QPushButton:hover {background-color: rgba(255, 255, 255, 0.50);}")
            self.trend_label.setStyleSheet("background-color: #333; color: white; padding: 20px; border-radius: 10px;")
            self.upcoming_label.setStyleSheet("background-color: #121212; color: white;")
            self.pending_label.setStyleSheet("background-color: #121212; color: white;")
            for btn in self.sidebar_buttons:
                btn.setStyleSheet("QPushButton {background: #121212; color: white; font-weight: bold; border: 1px solid black; border-radius: 15px; text-align: center; padding: 2px 12px; font-family: Gabriola;} QPushButton:hover {background-color: rgba(255, 255, 255, 0.50);}")
            for label in self.dynamic_labels:
                label.setStyleSheet("background-color: #1e1e1e; color: white; padding: 20px; border-radius: 10px;")
            self.dark_mode = True

    def create_bar_chart(self):
        if hasattr(self, 'bar_chart_canvas'):
            self.chart_layout.removeWidget(self.bar_chart_canvas)
            self.bar_chart_canvas.setParent(None)

        # Create new figure and axis
        self.figure = Figure(figsize=(5, 2), dpi=100)
        ax = self.figure.add_subplot(111)

        # Example data
        categories = ['Batch A', 'Batch B', 'Batch C', 'Batch D', 'Batch E']
        values = [15, 30, 10, 25, 20]
        bar_colors = ['#b60338', '#d95d39', '#f2a541', '#77b6ea', '#4a7c59']

        # Plotting the bar chart
        bars = ax.bar(categories, values, color=bar_colors)

        # Adding data labels
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=9)

        ax.set_ylabel('Per month')
        ax.set_title(' Monthly Batch Overview')
        ax.set_facecolor('none')

        self.bar_chart_canvas = FigureCanvas(self.figure)
        self.chart_layout.addWidget(self.bar_chart_canvas)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec_())
