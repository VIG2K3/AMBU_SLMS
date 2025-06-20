import sys
import sqlite3
import os
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QSizePolicy, QHeaderView,
    QMessageBox, QDialog, QFormLayout, QLineEdit, QSpinBox
)
from PyQt5.QtCore import Qt

DB_FILE = 'inventory.db'

def setup_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            p_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            name TEXT,
            qty INTEGER,
            expiry TEXT,
            email TEXT,
            barcode TEXT,
            created_date TEXT,
            status TEXT
        )
    ''')
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        products = [
            ('Dairy', 'Milk', 50, '2025-06-15', 'supplier1@example.com', '123456789012', '2025-01-01', ''),
            ('Eggs', 'Eggs', 200, '2025-06-13', 'supplier2@example.com', '987654321098', '2025-02-15', ''),
            ('Dairy', 'Cheese', 20, '2025-05-10', 'supplier3@example.com', '112233445566', '2025-03-10', '')
        ]
        cursor.executemany('''
            INSERT INTO products 
            (category, name, qty, expiry, email, barcode, created_date, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', products)
        conn.commit()
    conn.close()

def update_statuses():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    today = datetime.now().date()

    cursor.execute("SELECT p_id, expiry FROM products")
    for p_id, expiry_str in cursor.fetchall():
        expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
        if expiry_date < today:
            status = 'Expired'
        elif expiry_date <= today + timedelta(days=3):
            status = 'Nearing Expiry'
        else:
            status = 'Fresh'
        cursor.execute("UPDATE products SET status = ? WHERE p_id = ?", (status, p_id))

    conn.commit()
    conn.close()

def fetch_products():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p_id, category, name, qty, expiry, email, barcode, created_date, status
        FROM products
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows

def save_product_changes(product):
    try:
        int(product[3])  # qty
        datetime.strptime(product[4], "%Y-%m-%d")
        datetime.strptime(product[7], "%Y-%m-%d")
    except Exception as e:
        return False, f"Validation error: {e}"

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE products SET
                category = ?, name = ?, qty = ?,
                expiry = ?, email = ?, barcode = ?, created_date = ?
            WHERE p_id = ?
        ''', (product[1], product[2], int(product[3]), product[4], product[5], product[6], product[7], product[0]))
        conn.commit()
    except Exception as e:
        conn.close()
        return False, str(e)
    conn.close()
    return True, "Saved successfully"

def add_product(product):
    try:
        int(product['qty'])
        datetime.strptime(product['expiry'], "%Y-%m-%d")
        datetime.strptime(product['created_date'], "%Y-%m-%d")
    except Exception as e:
        return False, f"Validation error: {e}"

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO products
            (category, name, qty, expiry, email, barcode, created_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, '')
        ''', (
            product['category'], product['name'], int(product['qty']),
            product['expiry'], product['email'], product['barcode'], product['created_date']
        ))
        conn.commit()
    except Exception as e:
        conn.close()
        return False, str(e)
    conn.close()
    return True, "Product added successfully"

def delete_products(p_ids):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.executemany("DELETE FROM products WHERE p_id = ?", [(p,) for p in p_ids])
        conn.commit()
    except Exception as e:
        conn.close()
        return False, str(e)
    conn.close()
    return True, "Deleted successfully"

class AddProductDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add New Product")
        self.layout = QFormLayout(self)

        self.category = QLineEdit()
        self.name = QLineEdit()
        self.qty = QSpinBox()
        self.qty.setMaximum(1000000)
        self.expiry = QLineEdit()
        self.expiry.setPlaceholderText("YYYY-MM-DD")
        self.email = QLineEdit()
        self.barcode = QLineEdit()
        self.created_date = QLineEdit()
        self.created_date.setPlaceholderText("YYYY-MM-DD")

        self.layout.addRow("Category:", self.category)
        self.layout.addRow("Name:", self.name)
        self.layout.addRow("Quantity:", self.qty)
        self.layout.addRow("Expiry Date:", self.expiry)
        self.layout.addRow("Email:", self.email)
        self.layout.addRow("Barcode:", self.barcode)
        self.layout.addRow("Created Date:", self.created_date)

        self.buttons_layout = QHBoxLayout()
        self.ok_btn = QPushButton("Add")
        self.cancel_btn = QPushButton("Cancel")
        self.buttons_layout.addWidget(self.ok_btn)
        self.buttons_layout.addWidget(self.cancel_btn)
        self.layout.addRow(self.buttons_layout)

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_data(self):
        return {
            'category': self.category.text(),
            'name': self.name.text(),
            'qty': self.qty.value(),
            'expiry': self.expiry.text(),
            'email': self.email.text(),
            'barcode': self.barcode.text(),
            'created_date': self.created_date.text()
        }

class ShelfLifeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shelf Life Management - PyQt5")
        self.resize(1100, 600)

        self.layout = QVBoxLayout()
        self.label = QLabel("Product Shelf Life Overview")
        self.layout.addWidget(self.label)

        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)

        # Buttons layout
        self.buttons_layout = QHBoxLayout()

        self.update_button = QPushButton("Update Statuses")
        self.update_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.update_button.clicked.connect(self.update_and_reload)
        self.buttons_layout.addWidget(self.update_button)

        self.save_button = QPushButton("Save Changes")
        self.save_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.save_button.clicked.connect(self.save_changes)
        self.buttons_layout.addWidget(self.save_button)

        self.add_button = QPushButton("Add New Product")
        self.add_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.add_button.clicked.connect(self.add_new_product)
        self.buttons_layout.addWidget(self.add_button)

        self.delete_button = QPushButton("Delete Selected Product(s)")
        self.delete_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.delete_button.clicked.connect(self.delete_selected_products)
        self.buttons_layout.addWidget(self.delete_button)

        self.layout.addLayout(self.buttons_layout)
        self.setLayout(self.layout)

        self.load_data()

    def load_data(self):
        products = fetch_products()
        self.table.setRowCount(len(products))
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            'P Id', 'Category', 'Name', 'Qty', 'Expiry',
            'Email', 'Barcode', 'Created Date', 'Status'
        ])

        for row_idx, (
            p_id, category, name, qty, expiry,
            email, barcode, created_date, status
        ) in enumerate(products):
            item = QTableWidgetItem(str(p_id))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 0, item)

            self.table.setItem(row_idx, 1, QTableWidgetItem(category))
            self.table.setItem(row_idx, 2, QTableWidgetItem(name))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(qty)))
            self.table.setItem(row_idx, 4, QTableWidgetItem(expiry))
            self.table.setItem(row_idx, 5, QTableWidgetItem(email))
            self.table.setItem(row_idx, 6, QTableWidgetItem(barcode))
            self.table.setItem(row_idx, 7, QTableWidgetItem(created_date))

            status_item = QTableWidgetItem(status if status else "")
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
            if status == "Expired":
                status_item.setBackground(Qt.red)
            elif status == "Nearing Expiry":
                status_item.setBackground(Qt.yellow)
            elif status == "Fresh":
                status_item.setBackground(Qt.green)
            self.table.setItem(row_idx, 8, status_item)

        self.table.resizeRowsToContents()

    def update_and_reload(self):
        update_statuses()
        self.load_data()

    def save_changes(self):
        rows = self.table.rowCount()
        columns = self.table.columnCount()
        errors = []
        for row in range(rows):
            product = []
            for col in range(columns):
                item = self.table.item(row, col)
                product.append(item.text() if item else "")
            success, msg = save_product_changes(product)
            if not success:
                errors.append(f"Row {row+1}: {msg}")

        if errors:
            QMessageBox.warning(self, "Save Errors", "\n".join(errors))
        else:
            QMessageBox.information(self, "Success", "All changes saved successfully!")
            self.update_and_reload()

    def add_new_product(self):
        dialog = AddProductDialog()
        if dialog.exec() == QDialog.Accepted:
            product_data = dialog.get_data()
            success, msg = add_product(product_data)
            if success:
                QMessageBox.information(self, "Success", msg)
                self.update_and_reload()
            else:
                QMessageBox.warning(self, "Error Adding Product", msg)

    def delete_selected_products(self):
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            QMessageBox.warning(self, "No selection", "Please select at least one row to delete.")
            return
        rows_to_delete = set()
        for sel in selected_ranges:
            for row in range(sel.topRow(), sel.bottomRow() + 1):
                rows_to_delete.add(row)

        p_ids = []
        for row in rows_to_delete:
            item = self.table.item(row, 0)  # p_id is column 0
            if item:
                p_ids.append(int(item.text()))

        if not p_ids:
            QMessageBox.warning(self, "No valid rows", "Could not find valid product IDs to delete.")
            return

        confirm = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete {len(p_ids)} product(s)?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            success, msg = delete_products(p_ids)
            if success:
                QMessageBox.information(self, "Deleted", msg)
                self.update_and_reload()
            else:
                QMessageBox.warning(self, "Error Deleting", msg)

if __name__ == "__main__":
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    setup_database()

    app = QApplication(sys.argv)

    # Apply your color theme
    app.setStyleSheet("""
        QWidget {
            background-color: #d9d9d9;
            font-family: Segoe UI, sans-serif;
        }
        
        QPushButton {
            background-color: #b60338;
            color: white;
            padding: 6px 12px;
            border-radius: 6px;
        }

        QPushButton:hover {
            background-color: #f31659;
        }

        QTableWidget {
            background-color: white;
            gridline-color: #b60338;
        }

        QHeaderView::section {
            background-color: #b60338;
            color: white;
            font-weight: bold;
            padding: 4px;
        }

        QLineEdit, QSpinBox {
            background-color: white;
            padding: 4px;
            border: 1px solid #ccc;
        }

        QLabel {
            font-weight: bold;
            color: #333;
        }
    """)

    window = ShelfLifeApp()
    window.showMaximized()  # Or use showFullScreen() if preferred
    sys.exit(app.exec_())
