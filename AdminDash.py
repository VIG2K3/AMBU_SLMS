import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QFrame, QMessageBox, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor
from PyQt5.QtCore import Qt, QTimer, QDateTime, pyqtSignal, QSize, QPropertyAnimation, QRect
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Import Other GUI
from employee import ProductOwnerRegistration
from ProductAdmin import ProductManager
from Approval import ApprovalsWidget
from Reports import ReportWidget


class Dashboard(QWidget):
    logout_signal = pyqtSignal()  # Signal to login page logout
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ambu - SLMS")
        self.resize(1900, 1000)
        self.setMinimumSize(1000, 600)
        self.setWindowIcon(QIcon("images/ambu_icon.png"))
        self.setStyleSheet("background-color: #d9d9d9;")
        self.dark_mode = False
        self.sidebar_buttons = []
        self.dynamic_labels = []
        self.tables = []
        self.initUI()

    def toggle_sidebar(self):
        current_width = self.sidebar_container.width()
        new_width = 0 if current_width > 0 else 400

        self.animation = QPropertyAnimation(self.sidebar_container, b"maximumWidth")
        self.animation.setDuration(300)
        self.animation.setStartValue(current_width)
        self.animation.setEndValue(new_width)
        self.animation.start()

        if current_width > 0:
            self.toggle_button.setText("☰")
        else:
            self.toggle_button.setText("<")

    def show_homepage(self):
        self.hide_all_internal_views() # Show approval table on homepage
        self.stats_container.setVisible(True)
        self.pie_chart_frame.setVisible(True)
        self.bar_chart_frame.setVisible(True)
        self.approval_table.setVisible(True)  
        self.pending_label.setVisible(True)

    def open_product_widget(self):
        self.hide_all_internal_views()

        if hasattr(self, 'product_widget') and self.product_widget is not None:
            self.product_widget.setVisible(True)
        else:
            self.product_widget = ProductManager()
            self.main_content_layout.addWidget(self.product_widget)

    def open_approval_widget(self):
        self.hide_all_internal_views()
        if hasattr(self, 'approval_widget') and self.approval_widget is not None:
            self.approval_widget.setVisible(True)

    def open_employee_widget(self):
        self.hide_all_internal_views()

        if hasattr(self, 'employee_widget') and self.employee_widget is not None:
            self.employee_widget.setVisible(True)
        else:
            self.employee_widget = ProductOwnerRegistration()
            self.main_content_layout.addWidget(self.employee_widget)

    def open_report_widget(self):
        self.hide_all_internal_views()

        if hasattr(self, 'report_widget') and self.report_widget is not None:
            self.report_widget.setVisible(True)
        else:
            self.report_widget = ReportWidget()
            self.main_content_layout.addWidget(self.report_widget)

    def hide_all_internal_views(self):
        widgets_to_hide = [
            "employee_widget",
            "product_widget",
            "report_widget",
            "batch_widget",
            "approval_widget"
        ]
        for attr in widgets_to_hide:
            widget = getattr(self, attr, None)
            if widget is not None:
                widget.setVisible(False)

        # Hide homepage charts and approval table
        self.stats_container.setVisible(False) # Hide it by default
        self.pie_chart_frame.setVisible(False)
        self.bar_chart_frame.setVisible(False)
        self.approval_table.setVisible(False)  
        self.pending_label.setVisible(False)
        
    def initUI(self):
        # Title bar spacing
        main_layout = QVBoxLayout(self)
        title_bar = QWidget()
        title_bar.setFixedHeight(80)
        self.title_bar = title_bar
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        self.active_sidebar_button = None

        # Logo
        self.logo_label = QLabel()
        self.logo_label.setPixmap(QPixmap("images/ambu_logo.png").scaled(250, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_label.setFixedSize(250, 80)
        title_layout.addWidget(self.logo_label)

        # Title
        self.title_text = QLabel("SHELF LIFE MANAGEMENT")
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
                    background-color: #f5f5f5;
                    color: black;
                    border-radius: 20px;
                    font-size: 18px;
                    border: 1px solid black;
                    font-weight: bold;
                    font-family: Gabriola;
                    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
                }
                QPushButton:hover {
                    background-color: #121212;
                    color: white;
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
            background-color: #f5f5f5;
            color: black;
            border-radius: 20px;
            font-size: 18px;
            border: 1px solid black;
            font-weight: bold;
            font-family: Gabriola;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
        }
        QPushButton:hover {
            background-color: #da0041;
            color: white;
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

        # Sidebar container (collapsible)
        self.sidebar_container = QFrame()
        self.sidebar_container.setMaximumWidth(400)
        self.sidebar_container.setStyleSheet("background-color: #b60338; border-radius: 15px;")
        sidebar_main_layout = QVBoxLayout(self.sidebar_container)
        sidebar_main_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_main_layout.setSpacing(0)

        # Top panel inside sidebar
        self.toggle_panel = QFrame()
        self.toggle_panel.setStyleSheet("background-color: #b60338; border-radius: 15px;")
        toggle_layout = QHBoxLayout(self.toggle_panel)
        toggle_layout.setContentsMargins(10, 10, 0, 10)

        # Menu title
        self.menu_title = QLabel("MENU")
        self.menu_title.setFont(QFont("Gabriola", 32, QFont.Bold))
        self.menu_title.setStyleSheet("color: white;")
        self.menu_title.setAlignment(Qt.AlignCenter)

        toggle_layout.addWidget(self.menu_title, 10)
        toggle_layout.addStretch()

        sidebar_main_layout.addWidget(self.toggle_panel)

        # Sidebar collapsible widget
        self.sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setContentsMargins(20, 0, 20, 0)
        sidebar_layout.setSpacing(10)
        self.sidebar_widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
                color: white;
            }
        """)
        # Sidebar button colour
        self.default_sidebar_style = """
               QPushButton {
                   text-align: left;
                   padding: 5px 30px;
                   color: black;
                   background: #f5f5f5;
                   border: none;
                   border-radius: 20px;
                   font-weight: bold;
                   font-family: Gabriola;
                   box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
               }
               QPushButton:hover {
                   background-color: #da0041;
                   color: white;
               }
               """

        self.active_sidebar_style = """
               QPushButton {
                   text-align: left;
                   padding: 5px 30px;
                   color: white;
                   background-color: #da0041;
                   border: none;
                   border-radius: 20px;
                   font-weight: bold;
                   font-family: Gabriola;
                   box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
               }
               """

        # Sidebar buttons with icons
        options = [
            ("HOMEPAGE", "images/home.png"),
            ("PRODUCT DETAILS", "images/product.png"),
            ("PENDING APPROVALS", "images/approval.png"),
            ("PRODUCT OWNERS", "images/employee.png"),
            ("REPORTS", "images/report.png")

        ]
        self.sidebar_buttons = []

        for label, icon_file in options:
            btn = QPushButton(label)
            btn.setIcon(QIcon(icon_file))
            btn.setIconSize(QSize(30, 30))
            btn.setLayoutDirection(Qt.LeftToRight)
            btn.setStyleSheet(self.default_sidebar_style)
            btn.setFont(QFont("Gabriola", 20))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(50)

            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setOffset(2, 2)
            shadow.setColor(QColor(0, 0, 0, 100))
            btn.setGraphicsEffect(shadow)

            sidebar_layout.addWidget(btn)
            self.sidebar_buttons.append(btn)
            btn.clicked.connect(lambda _, b=btn, o=label: self.handle_sidebar_click(b, o))

        sidebar_layout.addStretch()
        sidebar_main_layout.addWidget(self.sidebar_widget)

        # Add sidebar to content layout
        content_layout.addWidget(self.sidebar_container, 1)

        # Main Content
        self.main_content_layout = QVBoxLayout()

        # Dash & Notification Bar (panel)
        top_bar = QHBoxLayout()

        # Toggle button
        self.toggle_button = QPushButton("<")
        self.toggle_button.setFixedSize(50, 50)
        self.toggle_button.setCursor(Qt.PointingHandCursor)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: black;
                font-size: 24px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da0041;
                color: white;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        top_bar.addWidget(self.toggle_button)

        # Dashboard title
        self.dash_title = QLineEdit()
        self.dash_title.setText("DASHBOARD")
        self.dash_title.setReadOnly(True)
        self.dash_title.setFixedHeight(30)
        self.dash_title.setStyleSheet("""
            border-radius: none;
            font-size: 35px;
            color: black;
            background-color: transparent;
            font-weight: bold;
            font-family: Gabriola;
        """)
        top_bar.addWidget(self.dash_title, 4)
        top_bar.addStretch()
        
        # Notification label and icon space
        notif_wrapper = QHBoxLayout()
        notif_wrapper.setSpacing(5)

        self.bell_text = QLabel("Notification")
        self.bell_text.setStyleSheet("font-size: 15px;")
        self.bell_text.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.notification_btn = QPushButton()
        self.notification_btn.setIcon(QIcon("images/bell_icon.png"))
        self.notification_btn.setIconSize(QSize(50, 50))
        self.notification_btn.setFixedSize(50, 50)
        self.notification_btn.setCursor(Qt.PointingHandCursor)
        self.notification_btn.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 25px;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #ffeb5b;
            }
        """)
        self.notification_btn.clicked.connect(self.open_notification_panel)

        notif_wrapper.addWidget(self.bell_text)
        notif_wrapper.addWidget(self.notification_btn)

        # Add the notif layout to the top bar
        top_bar.addLayout(notif_wrapper)

        # Add the top bar to the main layout
        self.main_content_layout.addLayout(top_bar)

        # Stats boxes
        self.stats_container = QWidget()
        stats_layout = QHBoxLayout(self.stats_container)  # Set layout during creation
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(10)

        for title in ["Total Batch", "Total Employees" ,"Pending Approvals", "Incoming Maturity"]:
            box = QVBoxLayout()
            lbl_title = QLabel(title)
            lbl_count = QLabel("0")

            lbl_title.setStyleSheet("color: black;")
            lbl_count.setStyleSheet("font-size: 18px; font-weight: bold;")

            box.addWidget(lbl_title)
            box.addWidget(lbl_count)

            box_frame = QFrame()
            box_frame.setLayout(box)
            box_frame.setFixedHeight(120)
            box_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    padding: 10px;
                    border-radius: 15px;
                }
            """)

            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setOffset(4, 4)
            shadow.setColor(QColor(0, 0, 0, 50))
            box_frame.setGraphicsEffect(shadow)

            stats_layout.addWidget(box_frame)

        self.main_content_layout.addWidget(self.stats_container)

        # Container for both charts
        chart_container = QWidget()
        chart_layout = QHBoxLayout(chart_container)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        chart_layout.setSpacing(5)

        # PIE CHART PANEL
        self.pie_chart_frame = QFrame()
        self.pie_chart_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
            }
        """)
        pie_shadow = QGraphicsDropShadowEffect()
        pie_shadow.setBlurRadius(20)
        pie_shadow.setOffset(4, 4)
        pie_shadow.setColor(QColor(0, 0, 0, 0))
        self.pie_chart_frame.setGraphicsEffect(pie_shadow)

        self.pie_chart_layout = QVBoxLayout(self.pie_chart_frame)
        self.pie_chart_layout.setContentsMargins(10, 10, 10, 10)
        self.create_pie_chart()

        # BAR CHART PANEL
        self.bar_chart_frame = QFrame()
        self.bar_chart_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
            }
        """)
        bar_shadow = QGraphicsDropShadowEffect()
        bar_shadow.setBlurRadius(25)
        bar_shadow.setOffset(4, 4)
        bar_shadow.setColor(QColor(0, 0, 0, 0))
        self.bar_chart_frame.setGraphicsEffect(bar_shadow)

        self.bar_chart_layout = QVBoxLayout(self.bar_chart_frame)
        self.bar_chart_layout.setContentsMargins(10, 10, 10, 10)
        self.create_bar_chart()

        # Add both to layout
        chart_layout.addWidget(self.pie_chart_frame, 1)
        chart_layout.addWidget(self.bar_chart_frame, 2)

        # Add to main layout
        self.main_content_layout.addWidget(chart_container)

        # Approval Table
        self.pending_label = QLabel("PENDING APPROVALS:")
        self.pending_label.setFont(QFont("Gabriola", 17, QFont.Bold))
        self.pending_label.setStyleSheet("color: black; background-color: transparent;")

        self.approval_table = QTableWidget(10, 6)
        self.approval_table.setHorizontalHeaderLabels(
            ["BATCH ID", "BATCH NAME", "QUANTITY", "IN DATE", "DUE DATE", "STATUS"])
        self.approval_table.verticalHeader().setVisible(False)
        self.approval_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.approval_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.approval_table.setFixedHeight(240)
        self.approval_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                color: black;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                color: black;
                font-size: 23px;
                font-weight: bold;
                font-family: Gabriola;
            }
        """)

        # Sample approval data
        sample_approvals = [
            ("REQ001", "", "Batch", "", "Pending"),
            ("REQ002", "", "Leave", "", "Approved"),
            ("REQ003", "", "Batch", "", "Rejected"),
            ("REQ004", "", "Leave", "", "Pending"),
            ("REQ005", "", "Batch", "", "Pending")
        ]

        for row, (req_id, name, req_type, date, status) in enumerate(sample_approvals):
            self.approval_table.setItem(row, 0, QTableWidgetItem(req_id))
            self.approval_table.setItem(row, 1, QTableWidgetItem(name))
            self.approval_table.setItem(row, 2, QTableWidgetItem(req_type))
            self.approval_table.setItem(row, 3, QTableWidgetItem(date))

            status_item = QTableWidgetItem(status)
            color = {"Pending": "orange", "Approved": "green", "Rejected": "red"}.get(status, "black")
            status_item.setForeground(QColor(color))
            self.approval_table.setItem(row, 4, status_item)

        # Create the approval widget page (used for Pending Approvals)
        self.approval_widget = ApprovalsWidget()
        self.main_content_layout.addWidget(self.approval_widget)
        self.approval_widget.setVisible(False)

        # Approval Table only used on homepage, added here and hidden initially
        self.main_content_layout.addWidget(self.pending_label)
        self.approval_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.main_content_layout.addWidget(self.approval_table)
        self.approval_table.setVisible(False)

        # Wrap up the main content widget
        self.content_widget = QWidget()
        self.content_widget.setLayout(self.main_content_layout)
        content_layout.addWidget(self.content_widget, 8)

        main_layout.addLayout(content_layout)

        self.footer = QLabel(None)
        self.footer.setFont(QFont("Times New Roman", 12))
        self.footer.setStyleSheet("background-color: #b60338; color: black;")
        self.footer.setAlignment(Qt.AlignCenter)
        self.footer.setFixedHeight(30)
        main_layout.addWidget(self.footer)

        self.show_homepage()

    def update_clock(self):
        current_datetime = QDateTime.currentDateTime()
        date_str = current_datetime.toString("dd-MM-yyyy")
        time_str = current_datetime.toString("HH:mm:ss")
        self.lbl_clock.setText(f"Date: {date_str}    Time: {time_str}")

    def open_notification_panel(self):
        QMessageBox.information(self, "Notifications", "No new notifications.")

    def handle_sidebar_click(self, button, option):
        for btn in self.sidebar_buttons:
            btn.setStyleSheet(self.default_sidebar_style)

        button.setStyleSheet(self.active_sidebar_style)
        self.active_sidebar_button = button

        if option == "HOMEPAGE":
            self.show_homepage()
        elif option == "PRODUCT DETAILS":
            self.open_product_widget()
        elif option == "PENDING APPROVALS":
            self.open_approval_widget()
        elif option == "PRODUCT OWNERS":
            self.open_employee_widget()
        elif option == "REPORTS":
            self.open_report_widget()

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
            self.logout_signal.emit()  # logout signal
            self.close()  # Close dashboard

    def toggle_theme(self):
        # Light Mode
        if self.dark_mode:
            self.setStyleSheet("background-color: #d9d9d9;")
            self.bell_text.setStyleSheet("color: black;")
            self.lbl_clock.setStyleSheet("background-color: #b60338; color: black;")
            self.sidebar_widget.setStyleSheet("background-color: #b60338; color: white; border-top-right-radius: 15px; border-bottom-right-radius: 15px;")
            self.toggle_panel.setStyleSheet("background-color: #b60338; border-radius: 15px;")
            self.sidebar_container.setStyleSheet("background-color: #b60338; border-radius: 15px;")
            self.footer.setStyleSheet("background-color: #b60338; color: black;")
            self.dash_title.setStyleSheet("border-radius: none; font-size: 35px; color: black; background-color: transparent; font-family: Gabriola;")
            self.title_text.setStyleSheet("color: black;")
            self.logout_btn.setStyleSheet("QPushButton {padding: 5px 15px; background-color: #f5f5f5; color: black; border-radius: 20px; font-size: 18px; border: 1px solid black; font-weight: bold; font-family: Gabriola; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);} QPushButton:hover {background-color: #da0041; color: white;}")
            self.theme_btn.setText("DARK MODE")
            self.theme_btn.setStyleSheet("QPushButton {padding: 5px 15px; background-color: #f5f5f5; color: black; border-radius: 20px; font-size: 18px; border: 1px solid black; font-weight: bold; font-family: Gabriola; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);} QPushButton:hover {background-color: #121212; color: white;}")
            for btn in self.sidebar_buttons:
                btn.setStyleSheet("QPushButton {background: #f5f5f5; color: black; font-weight: bold; border: none; border-radius: 20px; text-align: left; padding: 5px 30px; font-family: Gabriola; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);} QPushButton:hover {background-color: #da0041; color: white;}")
            for label in self.dynamic_labels:
                label.setStyleSheet("background-color: white; color: black; padding: 20px; border-radius: 10px;")
            self.dark_mode = False
        else:
            # Dark Mode
            self.setStyleSheet("background-color: #121212;")
            self.bell_text.setStyleSheet("color: white;")
            self.lbl_clock.setStyleSheet("background-color: #333; color: white;")
            self.sidebar_widget.setStyleSheet("background-color: #333; color: white; border-top-right-radius: 15px; border-bottom-right-radius: 15px;")
            self.toggle_panel.setStyleSheet("background-color: #333; border-radius: 15px;")
            self.sidebar_container.setStyleSheet("background-color: #333; border-radius: 15px;")
            self.footer.setStyleSheet("background-color: #333; color: white;")
            self.dash_title.setStyleSheet("border-radius: none; font-size: 35px; color: white; background-color: transparent; font-family: Gabriola;")
            self.title_text.setStyleSheet("color: white;")
            self.logout_btn.setStyleSheet("QPushButton {padding: 5px 15px; background-color: #f5f5f5; color: black; border-radius: 20px; font-size: 18px; border: 1px solid black; font-weight: bold; font-family: Gabriola; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);} QPushButton:hover {background-color: #da0041; color: white;}")
            self.theme_btn.setText("LIGHT MODE")
            self.theme_btn.setStyleSheet("QPushButton {padding: 5px 15px; background-color: #333; color: white; border-radius: 20px; font-size: 18px; border: 1px solid black; font-weight: bold; font-family: Gabriola; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);} QPushButton:hover {background-color: white; color: black;}")
            for btn in self.sidebar_buttons:
                btn.setStyleSheet("QPushButton {background: #121212; color: white; font-weight: bold; border: none; border-radius: 20px; text-align: left; padding: 5px 30px; font-family: Gabriola; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);} QPushButton:hover {background-color: rgba(255, 255, 255, 0.40); color: black;}")
            for label in self.dynamic_labels:
                label.setStyleSheet("background-color: #1e1e1e; color: white; padding: 20px; border-radius: 10px;")
            self.dark_mode = True

    def create_pie_chart(self):
        self.pie_figure = Figure(figsize=(4, 4), dpi=100)
        ax = self.pie_figure.add_subplot(111)
        self.pie_figure.subplots_adjust(top=0.80)

        labels = ['Approved', 'Pending', 'Rejected']
        sizes = [45, 35, 20]
        colors = ['#77b6ea', '#d95d39', '#b60338']
        explode = (0.05, 0.05, 0.05)

        wedges, texts, autotexts = ax.pie(
            sizes,
            explode=explode,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            shadow=True,
            startangle=140,
            textprops={'color': 'black', 'fontsize': 10, 'fontname': 'Segoe UI'}
        )

        for t in texts + autotexts:
            t.set_fontname("Segoe UI")

        ax.set_title("APPROVAL REQUEST", fontweight="bold", fontsize=12, pad=20, fontname="Segoe UI")
        ax.axis('equal')

        canvas = FigureCanvas(self.pie_figure)
        self.pie_chart_layout.addWidget(canvas)

    def create_bar_chart(self):
        if hasattr(self, 'bar_chart_canvas'):
            self.bar_chart_layout.removeWidget(self.bar_chart_canvas)
            self.bar_chart_canvas.setParent(None)

        self.figure = Figure(figsize=(5, 3), dpi=100)
        ax = self.figure.add_subplot(111)

        categories = list(range(1, 11))
        activity = [20, 35, 30, 35, 27, 25, 40, 45, 38, 42]
        goal = [34, 40, 50, 45, 30, 35, 50, 50, 45, 48]

        bar_width = 0.35
        x_indexes = range(len(categories))

        activity_color = '#b60338'
        goal_color = '#d9d9d9'

        ax.bar([x - bar_width / 2 for x in x_indexes], activity, width=bar_width, label="Test1",
               color=activity_color)
        ax.bar([x + bar_width / 2 for x in x_indexes], goal, width=bar_width, label="Test2", color=goal_color)

        ax.set_xticks(x_indexes)
        ax.set_xticklabels(categories)
        ax.set_title(" MONTHLY BATCH", fontweight='bold', fontsize=12, fontname="Segoe UI")
        ax.legend(loc='upper right')
        ax.grid(axis='y', linestyle='--', alpha=0.3)

        ax.set_facecolor("white")
        self.figure.patch.set_facecolor("white")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        self.bar_chart_canvas = FigureCanvas(self.figure)
        self.bar_chart_layout.addWidget(self.bar_chart_canvas)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.showFullScreen()
    sys.exit(app.exec_())
