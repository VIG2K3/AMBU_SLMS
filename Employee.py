import sys
import sqlite3
import csv
import hashlib
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLineEdit, QLabel, QMessageBox,
    QComboBox, QFileDialog, QInputDialog, QHeaderView, QCheckBox
)
from PyQt5.QtCore import Qt

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class EmployeeRegistration(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Employee Registration System")
        self.resize(1000, 600)
        self.selected_emp_id = None
        self.setup_ui()
        self.create_table()
        self.load_data()

    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                font-family: Arial;
                font-size: 16px;
                background-color: #d9d9d9;
            }
            QPushButton {
                background-color: #b60338;
                color: #d9d9d9;
                padding: 5px 15px;
                border-radius: 5px;
                border: 1px solid black; 
            }
            QPushButton:hover {
                background-color: #f31659;
            }
            QLineEdit, QComboBox {
                padding: 4px;
                background-color: white;
                border: 1px solid black;
                border-radius: 4px;
            }
        """)

        main_layout = QVBoxLayout()

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["EMP ID", "FIRST NAME", "LAST NAME", "USERNAME", "PASSWORD", "ROLE"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.cellClicked.connect(self.load_selected_row)
        main_layout.addWidget(self.table)

        # Input Fields
        form_layout = QHBoxLayout()
        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.toggle_password_checkbox = QCheckBox("Show Password")
        self.toggle_password_checkbox.toggled.connect(self.toggle_password_visibility)

        self.role_input = QComboBox()
        self.role_input.addItems(["Admin", "Employee"])

        form_layout.addWidget(QLabel("First Name"))
        form_layout.addWidget(self.first_name_input)
        form_layout.addWidget(QLabel("Last Name"))
        form_layout.addWidget(self.last_name_input)
        form_layout.addWidget(QLabel("Username"))
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(QLabel("Password"))
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.toggle_password_checkbox)
        form_layout.addWidget(QLabel("Role"))
        form_layout.addWidget(self.role_input)

        main_layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_employee)

        self.update_button = QPushButton("Update")
        self.update_button.clicked.connect(self.update_employee)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_employee)

        self.export_button = QPushButton("Export To Excel")
        self.export_button.clicked.connect(self.export_to_excel)

        self.reset_button = QPushButton("Reset Password")
        self.reset_button.clicked.connect(self.reset_password)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.reset_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def toggle_password_visibility(self, checked):
        self.password_input.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)

    def create_table(self):
        conn = sqlite3.connect("employees.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                empID INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def load_data(self):
        self.table.setRowCount(0)
        conn = sqlite3.connect("employees.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees")
        for row_data in cursor.fetchall():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, data in enumerate(row_data):
                self.table.setItem(row, col, QTableWidgetItem(str(data)))
        conn.close()

    def load_selected_row(self, row, column):
        self.selected_emp_id = self.table.item(row, 0).text()
        self.first_name_input.setText(self.table.item(row, 1).text())
        self.last_name_input.setText(self.table.item(row, 2).text())
        self.username_input.setText(self.table.item(row, 3).text())
        self.password_input.clear()
        self.toggle_password_checkbox.setChecked(False)
        self.role_input.setCurrentText(self.table.item(row, 5).text())

    def add_employee(self):
        first = self.first_name_input.text()
        last = self.last_name_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        role = self.role_input.currentText()

        if not all([first, last, username, password]):
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        if len(password) < 8:
            QMessageBox.warning(self, "Input Error", "Password must be at least 8 characters long.")
            return

        hashed = hash_password(password)
        try:
            conn = sqlite3.connect("employees.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO employees (first_name, last_name, username, password, role) VALUES (?, ?, ?, ?, ?)",
                           (first, last, username, hashed, role))
            conn.commit()
            conn.close()
            self.load_data()
            self.clear_fields()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Username already exists.")

    def update_employee(self):
        if not self.selected_emp_id:
            QMessageBox.warning(self, "Selection Error", "Please select a row to update.")
            return

        first = self.first_name_input.text()
        last = self.last_name_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        role = self.role_input.currentText()

        if not all([first, last, username]):
            QMessageBox.warning(self, "Input Error", "First name, last name and username are required.")
            return

        conn = sqlite3.connect("employees.db")
        cursor = conn.cursor()

        if password:
            if len(password) < 8:
                QMessageBox.warning(self, "Input Error", "Password must be at least 8 characters long.")
                return
            hashed = hash_password(password)
            cursor.execute(
                "UPDATE employees SET first_name=?, last_name=?, username=?, password=?, role=? WHERE empID=?",
                (first, last, username, hashed, role, self.selected_emp_id))
        else:
            cursor.execute("UPDATE employees SET first_name=?, last_name=?, username=?, role=? WHERE empID=?",
                           (first, last, username, role, self.selected_emp_id))

        conn.commit()
        conn.close()
        self.load_data()
        self.clear_fields()

    def delete_employee(self):
        if not self.selected_emp_id:
            QMessageBox.warning(self, "Selection Error", "Please select a row to delete.")
            return

        conn = sqlite3.connect("employees.db")
        cursor = conn.cursor()

        # Get total number of users
        cursor.execute("SELECT COUNT(*) FROM employees")
        total_users = cursor.fetchone()[0]

        # Get role of the selected employee
        cursor.execute("SELECT role FROM employees WHERE empID=?", (self.selected_emp_id,))
        result = cursor.fetchone()
        if not result:
            QMessageBox.warning(self, "Error", "Selected employee not found.")
            conn.close()
            return
        selected_role = result[0]

        # Count total Admins
        cursor.execute("SELECT COUNT(*) FROM employees WHERE role='Admin'")
        total_admins = cursor.fetchone()[0]
        conn.close()

        # Block deletion if it's the only account
        if total_users <= 1:
            QMessageBox.warning(self, "Deletion Denied", "At least one account must remain in the system.")
            return

        # Block deletion if it's the last Admin
        if selected_role == "Admin" and total_admins <= 1:
            QMessageBox.warning(self, "Deletion Denied", "At least one Admin must remain in the system.")
            return

        # Confirm deletion
        confirm = QMessageBox.question(self, "Delete", "Are you sure you want to delete this employee?")
        if confirm == QMessageBox.Yes:
            conn = sqlite3.connect("employees.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM employees WHERE empID=?", (self.selected_emp_id,))
            conn.commit()
            conn.close()
            self.load_data()
            self.clear_fields()

    def export_to_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "employees.csv", "CSV Files (*.csv)")
        if path:
            try:
                conn = sqlite3.connect("employees.db")
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM employees")
                records = cursor.fetchall()
                conn.close()

                with open(path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["empID", "first_name", "last_name", "username", "password", "role"])
                    writer.writerows(records)

                QMessageBox.information(self, "Export Successful", f"Data exported to {path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Failed", f"An error occurred: {str(e)}")

    def reset_password(self):
        if not self.selected_emp_id:
            QMessageBox.warning(self, "No Selection", "Please select an employee to reset their password.")
            return

        new_password, ok = QInputDialog.getText(self, "Reset Password", "Enter new password:", QLineEdit.Password)
        if ok and new_password:
            if len(new_password) < 8:
                QMessageBox.warning(self, "Input Error", "Password must be at least 8 characters long.")
                return
            hashed = hash_password(new_password)
            try:
                conn = sqlite3.connect("employees.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE employees SET password=? WHERE empID=?", (hashed, self.selected_emp_id))
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Success", "Password reset successfully.")
                self.clear_fields()
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to reset password: {str(e)}")

    def clear_fields(self):
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.username_input.clear()
        self.password_input.clear()
        self.role_input.setCurrentIndex(0)
        self.toggle_password_checkbox.setChecked(False)
        self.selected_emp_id = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmployeeRegistration()
    window.showMaximized()
    sys.exit(app.exec_())
