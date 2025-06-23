import sys
import sqlite3
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QDateEdit
)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QColor

# ------------------------- DATABASE MANAGER -------------------------

class DatabaseManager:
    def __init__(self, db_file="Product.db"):
        self.conn = sqlite3.connect(db_file)
        self.create_tables()

    def create_tables(self):
        sql = '''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                quantity INTEGER NOT NULL,
                supplier_email TEXT NOT NULL,
                barcode TEXT UNIQUE,
                test_date TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL
            )
        '''
        self.conn.execute(sql)
        self.conn.commit()

    def get_all_products(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products ORDER BY id")
        return cursor.fetchall()

    def delete_product(self, product_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        self.conn.commit()
        return cursor.rowcount

# ------------------------- REPORT SYSTEM -------------------------

report_conn = sqlite3.connect("report_system.db")
report_cursor = report_conn.cursor()
report_cursor.execute('''
    CREATE TABLE IF NOT EXISTS history_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        quantity INTEGER NOT NULL,
        supplier_email TEXT NOT NULL,
        barcode TEXT,
        test_date TEXT,
        created_date TEXT,
        status TEXT NOT NULL,
        moved_date TEXT
    )
''')
report_conn.commit()

class ReportSystem(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Report and Due Date System")
        self.setGeometry(100, 100, 1200, 600)

        self.product_db = DatabaseManager("Product.db")

        layout = QVBoxLayout()
        self.tabs = QTabWidget()

        self.active_tab = QWidget()
        self.history_tab = QWidget()

        self.init_active_tab()
        self.init_history_tab()

        self.tabs.addTab(self.active_tab, "Batch List")
        self.tabs.addTab(self.history_tab, "Report")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.load_active_items()
        self.load_history_items()

    def init_active_tab(self):
        layout = QVBoxLayout()

        self.active_table = QTableWidget()
        self.active_table.setColumnCount(10)
        self.active_table.setHorizontalHeaderLabels([
            "Product ID", "Product Category", "Product Name", "Description",
            "Quantity", "Email", "Barcode", "Test Date", "Created Date", "Status"
        ])
        self.active_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.active_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.active_table.setSelectionMode(QTableWidget.SingleSelection)

        # Header styling
        self.active_table.setStyleSheet("""
            QHeaderView::section {
                background-color: #f0f0f0;
                color: black;
                font-size: 15px;
                padding: 6px;
                border: 1px solid #ccc;
            }
        """)

        layout.addWidget(self.active_table)

        button_layout = QHBoxLayout()
        self.due_date_input = QDateEdit(calendarPopup=True)
        self.due_date_input.setDate(QDate.currentDate())
        self.due_date_input.setDisplayFormat("dd-MM-yyyy")

        move_button = QPushButton("Move to Report")
        move_button.setFixedSize(180, 40)
        move_button.setStyleSheet("""
            QPushButton {
                background-color: #b60338;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #da0041;
            }
        """)
        move_button.clicked.connect(self.move_selected_item)

        button_layout.addStretch()
        button_layout.addWidget(move_button)

        layout.addLayout(button_layout)
        self.active_tab.setLayout(layout)

    def init_history_tab(self):
        layout = QVBoxLayout()
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(10)
        self.history_table.setHorizontalHeaderLabels([
            "Product Category", "Product Name", "Description", "Quantity", "Email",
            "Barcode", "Test Date", "Created Date", "Status", "Moved Date"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Header styling for history tab
        self.history_table.setStyleSheet("""
            QHeaderView::section {
                background-color: #f0f0f0;
                color: black;
                font-size: 15px;
                padding: 6px;
                border: 1px solid #ccc;
            }
        """)

        layout.addWidget(self.history_table)
        self.history_tab.setLayout(layout)

    def move_selected_item(self):
        selected_items = self.active_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a product row to transfer.")
            return

        row = selected_items[0].row()
        product_id = int(self.active_table.item(row, 0).text())
        name = self.active_table.item(row, 2).text()
        category = self.active_table.item(row, 1).text()
        due_date_str = self.active_table.item(row, 7).text()

        confirm = QMessageBox.question(self, "Confirm Transfer",
                                       f"Are you sure you want to remove '{name}' from batch details and move it to report?",
                                       QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.Yes:
            try:
                due_date = datetime.strptime(due_date_str, "%d-%m-%Y")
            except:
                QMessageBox.warning(self, "Error", "Invalid test date format.")
                return

            self.move_to_history(product_id, name, category, due_date)

    def load_active_items(self):
        self.active_table.setRowCount(0)
        products = self.product_db.get_all_products()

        for row_data in products:
            pid = row_data[0]
            category = row_data[1]
            product_id = row_data[2]
            description = row_data[3]
            quantity = row_data[4]
            email = row_data[5]
            barcode = row_data[6]
            test_date = row_data[7]
            created_date = row_data[8]
            status = row_data[9]

            if not test_date:
                continue
            try:
                due_date = datetime.strptime(test_date, "%d-%m-%Y")
            except:
                continue

            if due_date <= datetime.today():
                self.move_to_history(pid, product_id, category, due_date)
                continue

            row_idx = self.active_table.rowCount()
            self.active_table.insertRow(row_idx)

            self.active_table.setItem(row_idx, 0, QTableWidgetItem(str(pid)))
            self.active_table.setItem(row_idx, 1, QTableWidgetItem(category))
            self.active_table.setItem(row_idx, 2, QTableWidgetItem(product_id))
            self.active_table.setItem(row_idx, 3, QTableWidgetItem(description))
            self.active_table.setItem(row_idx, 4, QTableWidgetItem(str(quantity)))
            self.active_table.setItem(row_idx, 5, QTableWidgetItem(email))
            self.active_table.setItem(row_idx, 6, QTableWidgetItem(barcode))
            self.active_table.setItem(row_idx, 7, QTableWidgetItem(test_date))
            self.active_table.setItem(row_idx, 8, QTableWidgetItem(created_date))
            self.active_table.setItem(row_idx, 9, QTableWidgetItem(status))

            bg_color = QColor("#ffffff") if row_idx % 2 == 0 else QColor("#f0f0f0")
            for col in range(10):
                self.active_table.item(row_idx, col).setBackground(bg_color)

    def load_history_items(self):
        self.history_table.setRowCount(0)
        report_cursor.execute("""
            SELECT category, name, description, quantity, supplier_email, barcode,
                   test_date, created_date, status, moved_date
            FROM history_items
        """)
        rows = report_cursor.fetchall()

        for row_idx, row_data in enumerate(rows):
            self.history_table.insertRow(row_idx)
            for col_idx in range(10):
                self.history_table.setItem(row_idx, col_idx, QTableWidgetItem(str(row_data[col_idx])))

    def reset_item(self, item_id):
        cursor = self.product_db.conn.cursor()
        cursor.execute("SELECT test_date FROM products WHERE id = ?", (item_id,))
        old_due_str = cursor.fetchone()[0]
        try:
            old_due = datetime.strptime(old_due_str, "%d-%m-%Y")
        except:
            old_due = datetime.today()
        new_due = (old_due + timedelta(days=30)).strftime("%d-%m-%Y")
        cursor.execute("UPDATE products SET test_date = ? WHERE id = ?", (new_due, item_id))
        self.product_db.conn.commit()
        self.load_active_items()

    def move_to_history(self, item_id, product_id, category, due_date):
        moved_date = datetime.today().strftime("%Y-%m-%d")
        cursor = self.product_db.conn.cursor()
        cursor.execute("""
            SELECT category, name, description, quantity, supplier_email, barcode,
                   test_date, created_date, status
            FROM products WHERE id = ?
        """, (item_id,))
        row = cursor.fetchone()

        if row:
            report_cursor.execute("""
                INSERT INTO history_items (category, name, description, quantity, supplier_email, barcode,
                                           test_date, created_date, status, moved_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (*row, moved_date))

        self.product_db.delete_product(item_id)
        report_conn.commit()
        self.load_active_items()
        self.load_history_items()

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = ReportSystem()
#     window.showMaximized()
#     sys.exit(app.exec_())
