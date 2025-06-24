import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QFrame, QMessageBox, QGraphicsDropShadowEffect,
    QCalendarWidget, QComboBox, QCheckBox, QFileDialog, QScrollArea, QTextEdit
)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QTextCharFormat, QBrush
from PyQt5.QtCore import Qt, QTimer, QDateTime, pyqtSignal, QSize, QPropertyAnimation, QRect, QDate
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime, timedelta
import sqlite3
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import MultipleLocator
import os
from collections import defaultdict

# Import Other GUI
from employee import ProductOwnerRegistration
from ProductAdmin import ProductManager
from Reports import ReportSystem


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
        new_width = 0 if current_width > 0 else 360

        self.animation = QPropertyAnimation(self.sidebar_container, b"maximumWidth")
        self.animation.setDuration(300)
        self.animation.setStartValue(current_width)
        self.animation.setEndValue(new_width)
        self.animation.start()

        # Optionally animate minimumWidth too for smoother resizing
        self.animation_min = QPropertyAnimation(self.sidebar_container, b"minimumWidth")
        self.animation_min.setDuration(300)
        self.animation_min.setStartValue(current_width)
        self.animation_min.setEndValue(new_width)
        self.animation_min.start()

        # Update toggle icon
        if current_width > 0:
            self.toggle_button.setText("☰")
        else:
            self.toggle_button.setText("<")

    def show_homepage(self):
        self.update_stats()
        self.refresh_bar_chart()
        self.refresh_pie_chart()
        self.hide_all_internal_views()
        self.stats_container.setVisible(True)
        self.pie_chart_frame.setVisible(True)
        self.bar_chart_frame.setVisible(True)
        self.calendar_frame.setVisible(True)
        self.notepad_panel.setVisible(True)

    def open_product_widget(self):
        self.hide_all_internal_views()

        if hasattr(self, 'product_widget') and self.product_widget is not None:
            self.product_widget.setVisible(True)
        else:
            self.product_widget = ProductManager(
                on_data_changed=self.update_stats,
                on_chart_refresh=lambda: self.refresh_all_charts()
            )
            self.main_content_layout.addWidget(self.product_widget)

    def open_employee_widget(self):
        self.hide_all_internal_views()

        if hasattr(self, 'employee_widget') and self.employee_widget is not None:
            self.employee_widget.setVisible(True)
        else:
            self.employee_widget = ProductOwnerRegistration()
            self.update_stats()
            self.main_content_layout.addWidget(self.employee_widget)

    def open_report_widget(self):
        self.hide_all_internal_views()

        if hasattr(self, 'report_widget') and self.report_widget is not None:
            self.report_widget.setVisible(True)
        else:
            self.report_widget = ReportSystem()
            self.main_content_layout.addWidget(self.report_widget)

    def hide_all_internal_views(self):
        widgets_to_hide = [
            "employee_widget",
            "product_widget",
            "report_widget"
        ]
        for attr in widgets_to_hide:
            widget = getattr(self, attr, None)
            if widget is not None:
                widget.setVisible(False)

        # Hide homepage charts and approval table
        self.stats_container.setVisible(False)
        self.pie_chart_frame.setVisible(False)
        self.bar_chart_frame.setVisible(False)
        self.calendar_frame.setVisible(False)
        self.notepad_panel.setVisible(False)


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
        self.sidebar_container.setMaximumWidth(0)
        self.sidebar_container.setMinimumWidth(0)
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
            ("BATCH DETAILS", "images/approval.png"),
            ("PRODUCT OWNER", "images/employee.png"),
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
        self.toggle_button = QPushButton("☰")
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

        # Profile button
        profileButton = QHBoxLayout()
        profileButton.setSpacing(8)

        self.profile_text = QLabel("Welcome,\nAdmin")
        self.profile_text.setStyleSheet("font-size: 14px; color: black; font-family: Arial;")
        self.profile_text.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.profile_icon = QLabel()
        pixmap = QPixmap("images/admin.png")
        self.profile_icon.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.profile_icon.setFixedSize(50, 50)
        self.profile_icon.setStyleSheet("border-radius: 25px; background-color: white;")

        # Add both to layout
        profileButton.addWidget(self.profile_text)
        profileButton.addWidget(self.profile_icon)

        # Add to top bar and main layout
        top_bar.addLayout(profileButton)
        self.main_content_layout.addLayout(top_bar)

        # Stats boxes
        self.stats_container = QWidget()
        stats_layout = QHBoxLayout(self.stats_container)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(10)

        for title in ["Total Batch", "Total Product Owner" ,"Pending Approvals", "Incoming Maturity"]:
            box = QVBoxLayout()
            self.lbl_title = QLabel(title)
            self.lbl_count = QLabel("0")

            self.lbl_title.setStyleSheet("color: black; font-size: 19px; font-family: Segoe UI;")
            self.lbl_count.setStyleSheet("color: black; font-size: 20px; font-weight: bold;")

            box.addWidget(self.lbl_title)
            box.addWidget(self.lbl_count)

            self.box_frame = QFrame()
            self.box_frame.setLayout(box)
            self.box_frame.setFixedHeight(140)
            self.box_frame.setStyleSheet("""
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
            self.box_frame.setGraphicsEffect(shadow)

            stats_layout.addWidget(self.box_frame)

        self.main_content_layout.addWidget(self.stats_container)

        # Chart Panel (Pie/Notepad/Calender)
        top_chart_layout = QHBoxLayout()
        top_chart_layout.setContentsMargins(0, 0, 0, 0)
        top_chart_layout.setSpacing(20)

        # Pie chart
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

        # Notepad
        self.notepad_panel = QFrame()
        self.notepad_panel.setMinimumSize(300, 300)
        self.notepad_panel.setMaximumWidth(500)
        self.notepad_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                color: black;
                border-radius: 15px;
            }
        """)
        notepad_shadow = QGraphicsDropShadowEffect()
        notepad_shadow.setBlurRadius(20)
        notepad_shadow.setOffset(4, 4)
        notepad_shadow.setColor(QColor(0, 0, 0, 100))
        self.notepad_panel.setGraphicsEffect(notepad_shadow)

        self.notepad_layout = QVBoxLayout(self.notepad_panel)
        self.notepad_layout.setContentsMargins(10, 10, 10, 10)

        self.notepad_textedit = QTextEdit()
        self.notepad_textedit.setPlaceholderText("Write your notes here...")
        self.notepad_textedit.setFont(QFont("Segoe UI", 11))

        self.save_button = QPushButton("Save Notes")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #b60338;
                color: white;
                border-radius: 5px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #d91e4b;
            }
        """)
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.clicked.connect(self.save_notes_to_file)

        self.notepad_layout.addWidget(self.notepad_textedit)
        self.notepad_layout.addWidget(self.save_button)

        # Calender Panel
        self.highlighted_dates = set()

        self.calendar_frame = QFrame()
        self.calendar_frame.setMinimumSize(300, 300)
        self.calendar_frame.setMaximumWidth(500)
        self.calendar_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
            }
        """)
        calendar_shadow = QGraphicsDropShadowEffect()
        calendar_shadow.setBlurRadius(20)
        calendar_shadow.setOffset(4, 4)
        calendar_shadow.setColor(QColor(0, 0, 0, 100))
        self.calendar_frame.setGraphicsEffect(calendar_shadow)

        calendar_layout = QVBoxLayout(self.calendar_frame)
        calendar_layout.setContentsMargins(10, 10, 10, 10)

        self.calendar_widget = QCalendarWidget()
        self.calendar_widget.setGridVisible(True)
        self.calendar_widget.setHorizontalHeaderFormat(QCalendarWidget.ShortDayNames)
        self.calendar_widget.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar_widget.setDateEditEnabled(False)
        self.calendar_widget.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
                border-radius: 10px;
                font-family: Segoe UI;
                font-size: 14px;
            }
            QCalendarWidget QToolButton {
                background-color: #d9d9d9;
                color: black;
                border-radius: 5px;
                padding: 5px;
            }
            QCalendarWidget QAbstractItemView:enabled {
                selection-background-color: #b60338;
                background-color: white;
                color: black;
            }
            QCalendarWidget QAbstractItemView::item:disabled {
                color: white;
            }
        """)
        calendar_layout.addWidget(self.calendar_widget)

        top_chart_layout.addWidget(self.pie_chart_frame, 1)
        top_chart_layout.addWidget(self.notepad_panel, 1)
        top_chart_layout.addWidget(self.calendar_frame, 1)
        self.main_content_layout.addLayout(top_chart_layout)

        # Bar chart
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

        self.bar_chart_layout = QVBoxLayout()
        self.bar_chart_frame.setLayout(self.bar_chart_layout)
        self.bar_chart_layout.setContentsMargins(10, 10, 10, 10)
        self.create_bar_chart()

        # Add bar chart to layout (below)
        self.main_content_layout.addWidget(self.bar_chart_frame)

        # Combine main content
        self.content_widget = QWidget()
        self.content_widget.setLayout(self.main_content_layout)
        content_layout.addWidget(self.content_widget, 8)
        main_layout.addLayout(content_layout)

        # Footer
        self.footer = QLabel(None)
        self.update_stats()
        self.footer.setFont(QFont("Times New Roman", 12))
        self.footer.setStyleSheet("background-color: #b60338; color: black;")
        self.footer.setAlignment(Qt.AlignCenter)
        self.footer.setFixedHeight(30)
        main_layout.addWidget(self.footer)

    def save_notes_to_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Notes", "notes.txt", "Text Files (*.txt);;All Files (*)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as file:
                    file.write(self.notepad_textedit.toPlainText())
                QMessageBox.information(self, "Saved", "Notes saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save notes:\n{str(e)}")

    def refresh_all_charts(self):
        self.refresh_bar_chart()
        self.refresh_pie_chart()

    def refresh_bar_chart(self):
        if not hasattr(self, 'bar_chart_layout'):
            print("bar_chart_layout does not exist yet.")
            return

        # Clear current chart
        for i in reversed(range(self.bar_chart_layout.count())):
            widget = self.bar_chart_layout.itemAt(i).widget()
            if widget is not None:
                self.bar_chart_layout.removeWidget(widget)
                widget.setParent(None)

        # Rebuild with live data
        self.create_bar_chart()

    def refresh_pie_chart(self):
        if not hasattr(self, 'pie_chart_layout'):
            print("pie_chart_layout does not exist yet.")
            return

        # Clear current pie chart
        for i in reversed(range(self.pie_chart_layout.count())):
            widget = self.pie_chart_layout.itemAt(i).widget()
            if widget is not None:
                self.pie_chart_layout.removeWidget(widget)
                widget.setParent(None)

        # Rebuild with live data
        self.create_pie_chart()

    def update_clock(self):
        current_datetime = QDateTime.currentDateTime()
        date_str = current_datetime.toString("dd-MM-yyyy")
        time_str = current_datetime.toString("HH:mm:ss")
        self.lbl_clock.setText(f"Date: {date_str}    Time: {time_str}")

    def handle_sidebar_click(self, button, option):
        for btn in self.sidebar_buttons:
            btn.setStyleSheet(self.default_sidebar_style)

        button.setStyleSheet(self.active_sidebar_style)
        self.active_sidebar_button = button

        if option == "HOMEPAGE":
            self.show_homepage()
        elif option == "BATCH DETAILS":
            self.open_product_widget()
        elif option == "PRODUCT OWNER":
            self.open_employee_widget()
        elif option == "REPORTS":
            self.open_report_widget()

    def update_stats(self):
        total_batch = 0
        total_product_owner = 0
        pending_approvals = 0
        incoming_maturity = 0

        try:
            conn = sqlite3.connect("Product.db")
            cur = conn.cursor()

            # Total approved (Total Batch)
            cur.execute("SELECT COUNT(*) FROM products WHERE status = 'Approved'")
            total_batch = cur.fetchone()[0]

            # Pending approvals
            cur.execute("SELECT COUNT(*) FROM products WHERE status = 'Pending'")
            pending_approvals = cur.fetchone()[0]

            # Incoming maturity (for 2 months/ approved)
            cur.execute(
                "SELECT test_date FROM products WHERE status = 'Approved' AND test_date IS NOT NULL AND test_date != ''")
            all_test_dates = cur.fetchall()
            today = datetime.today()
            in_60_days = today + timedelta(days=60)

            for (test_date_str,) in all_test_dates:
                try:
                    test_date = datetime.strptime(test_date_str, "%d-%m-%Y")
                    if today <= test_date <= in_60_days:
                        incoming_maturity += 1
                except ValueError:
                    continue

            conn.close()
        except Exception as e:
            print("Error updating product stats:", e)

        try:
            conn = sqlite3.connect("employees.db")
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM employees")
            total_product_owner = cur.fetchone()[0]
            conn.close()
        except:
            total_product_owner = 0

        # Update the stat box labels
        stat_titles = ["Total Batch", "Total Product Owner", "Pending Approvals", "Incoming Maturity"]
        stat_values = [total_batch, total_product_owner, pending_approvals, incoming_maturity]

        labels = self.stats_container.findChildren(QLabel)
        for i in range(len(labels)):
            if labels[i].text() in stat_titles:
                labels[i + 1].setText(str(stat_values[stat_titles.index(labels[i].text())]))

    def confirm_logout(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Logout")
        msg_box.setText("Are you sure you want to logout?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        if self.dark_mode:
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #d9d9d9;
                    color: white;
                    font-size: 16px;
                }
                QLabel {
                    background-color: #d9d9d9;
                    color: black;
                    font-size: 16px;
                }
                QPushButton {
                    background-color: #d9d9d9;
                    color: white;
                    padding: 6px 12px;
                    border: 1px solid white;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #3d3d3d;
                }
                QPushButton:pressed {
                    background-color: #555555;
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
            self.profile_text.setStyleSheet("color: black;")
            self.lbl_clock.setStyleSheet("background-color: #b60338; color: black;")
            self.sidebar_widget.setStyleSheet("background-color: #b60338; color: white; border-top-right-radius: 15px; border-bottom-right-radius: 15px;")
            self.toggle_panel.setStyleSheet("background-color: #b60338; border-radius: 15px;")
            self.sidebar_container.setStyleSheet("background-color: #b60338; border-radius: 15px;")

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
            self.toggle_button.setStyleSheet("""QPushButton {background-color: #f5f5f5;color: black;font-size: 24px;font-weight: bold;border: none;border-radius: 5px;}QPushButton:hover {background-color: #da0041;color: white;}""")
            self.footer.setStyleSheet("background-color: #b60338; color: black;")
            self.pie_chart_frame.setStyleSheet("""QFrame {background-color: white;border-radius: 15px;}""")
            self.save_button.setStyleSheet("""QPushButton {background-color: #b60338; color: white; border-radius: 5px; padding: 6px 12px;}QPushButton:hover {background-color: #d91e4b;}""")
            self.calendar_frame.setStyleSheet("""QFrame {background-color: white;border-radius: 15px;}""")
            self.bar_chart_frame.setStyleSheet("""QFrame {background-color: white;border-radius: 15px;}""")
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
            self.profile_text.setStyleSheet("color: white;")
            self.lbl_clock.setStyleSheet("background-color: #333; color: white;")
            self.sidebar_widget.setStyleSheet("background-color: #333; color: white; border-top-right-radius: 15px; border-bottom-right-radius: 15px;")
            self.toggle_panel.setStyleSheet("background-color: #333; border-radius: 15px;")
            self.sidebar_container.setStyleSheet("background-color: #333; border-radius: 15px;")

            self.default_sidebar_style = """
                           QPushButton {
                               text-align: left;
                               padding: 5px 30px;
                               color: white;
                               background: #121212;
                               border: none;
                               border-radius: 20px;
                               font-weight: bold;
                               font-family: Gabriola;
                               box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
                           }
                           QPushButton:hover {
                               background-color: background-color: rgba(255, 255, 255, 0.40);
                           }
                           """

            self.active_sidebar_style = """
                           QPushButton {
                               text-align: left;
                               padding: 5px 30px;
                               color: white;
                               background-color: rgba(255, 255, 255, 0.40);
                               border: none;
                               border-radius: 20px;
                               font-weight: bold;
                               font-family: Gabriola;
                               box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
                           }
                           """
            self.toggle_button.setStyleSheet("""QPushButton {background-color: white;color: black;font-size: 24px;font-weight: bold;border: none;border-radius: 5px;}QPushButton:hover {background-color: rgba(255, 255, 255, 0.40);color: white;}""")
            self.footer.setStyleSheet("background-color: #333; color: white;")
            self.pie_chart_frame.setStyleSheet("""QFrame {background-color: white; border-radius: 15px;}""")
            self.save_button.setStyleSheet("""QPushButton {background-color: black; color: white; border-radius: 5px; padding: 6px 12px;}QPushButton:hover {background-color: black; color: white;}""")
            self.bar_chart_frame.setStyleSheet("""QFrame {background-color: white ;border-radius: 15px;}""")
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
        if hasattr(self, 'pie_chart_canvas'):
            self.pie_chart_layout.removeWidget(self.pie_chart_canvas)
            self.pie_chart_canvas.setParent(None)

        self.pie_figure = Figure(figsize=(4, 4), dpi=100)
        ax = self.pie_figure.add_subplot(111)
        self.pie_figure.subplots_adjust(top=0.80)

        # Step 1: Fetch status counts from database
        status_counts = {"Approved": 0, "Pending": 0, "Rejected": 0}

        try:
            conn = sqlite3.connect("Product.db")
            cur = conn.cursor()
            cur.execute("SELECT status FROM products")
            results = cur.fetchall()
            conn.close()

            for (status,) in results:
                if status in status_counts:
                    status_counts[status] += 1
        except Exception as e:
            print("Error loading pie chart data:", e)

        labels = []
        sizes = []
        colors = []
        color_map = {
            "Approved": '#4a7c59',
            "Pending": '#f2a541',
            "Rejected": '#b60338'
        }

        for status, count in status_counts.items():
            if count > 0:
                labels.append(status)
                sizes.append(count)
                colors.append(color_map[status])

        if not sizes:
            labels = ['No Data']
            sizes = [1]
            colors = ['#cccccc']

        explode = [0.05] * len(sizes)

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

        ax.set_title("BATCH STATUS", fontweight="bold", fontsize=14, pad=20, fontname="Candara")
        ax.axis('equal')

        self.pie_chart_canvas = FigureCanvas(self.pie_figure)
        self.pie_chart_layout.addWidget(self.pie_chart_canvas)

    def create_bar_chart(self):
        if hasattr(self, 'bar_chart_canvas'):
            self.bar_chart_layout.removeWidget(self.bar_chart_canvas)
            self.bar_chart_canvas.setParent(None)

        self.figure = Figure(figsize=(5, 3), dpi=100)
        ax = self.figure.add_subplot(111)

        categories = []
        activity = []

        if os.path.exists("Product.db"):
            try:
                conn = sqlite3.connect("Product.db")
                cur = conn.cursor()

                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
                if cur.fetchone():
                    cur.execute("SELECT category, quantity FROM products WHERE status = 'Approved'")
                    results = cur.fetchall()

                    category_totals = defaultdict(int)
                    for row in results:
                        category, qty = row
                        try:
                            category_totals[category] += int(qty)
                        except:
                            continue

                    categories = list(category_totals.keys())
                    activity = list(category_totals.values())

                conn.close()
            except Exception as e:
                print("Error reading from Product.db:", e)

        if not categories:
            categories = ["No Data"]
            activity = [0]

        bar_width = 0.5
        x_indexes = range(len(categories))
        activity_color = '#4aadaa'

        ax.bar(x_indexes, activity, width=bar_width, label="CATEGORIES", color=activity_color)

        max_val = max(activity) if activity else 0
        lower = 0
        upper = ((max_val // 100) + 2) * 100 if max_val > 0 else 100
        ax.set_ylim(lower, upper)
        ax.yaxis.set_major_locator(MultipleLocator(100))

        ax.set_xticks(x_indexes)
        ax.set_xticklabels(categories, rotation=0, ha='center')
        ax.set_ylabel("TOTAL QUANTITY", fontweight="bold", fontsize=14, fontname="Candara")
        ax.set_title("BATCH DISTRIBUTION",fontweight="bold", fontsize=14, fontname="Candara")
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
