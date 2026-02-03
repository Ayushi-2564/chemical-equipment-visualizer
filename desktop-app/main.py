# desktop-app/main.py

import sys
import requests
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QTableWidget,
    QTableWidgetItem, QTabWidget, QMessageBox, QStackedWidget,
    QFormLayout, QGroupBox, QGridLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import json


API_URL = "http://localhost:8000/api"


class LoginWindow(QWidget):
    """Login/Register Window"""
    
    login_success = pyqtSignal(str, dict)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Chemical Equipment Visualizer - Login")
        self.setGeometry(100, 100, 400, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: Arial;
            }
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5568d3;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Chemical Equipment Visualizer")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #667eea; margin: 20px;")
        layout.addWidget(title)
        
        # Login Form
        login_group = QGroupBox("Login")
        login_layout = QFormLayout()
        
        self.login_username = QLineEdit()
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.Password)
        
        login_layout.addRow("Username:", self.login_username)
        login_layout.addRow("Password:", self.login_password)
        
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.handle_login)
        login_layout.addRow(login_btn)
        
        login_group.setLayout(login_layout)
        layout.addWidget(login_group)
        
        # Register Form
        register_group = QGroupBox("Register")
        register_layout = QFormLayout()
        
        self.register_username = QLineEdit()
        self.register_email = QLineEdit()
        self.register_password = QLineEdit()
        self.register_password.setEchoMode(QLineEdit.Password)
        self.register_confirm = QLineEdit()
        self.register_confirm.setEchoMode(QLineEdit.Password)
        
        register_layout.addRow("Username:", self.register_username)
        register_layout.addRow("Email:", self.register_email)
        register_layout.addRow("Password:", self.register_password)
        register_layout.addRow("Confirm:", self.register_confirm)
        
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.handle_register)
        register_layout.addRow(register_btn)
        
        register_group.setLayout(register_layout)
        layout.addWidget(register_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def handle_login(self):
        username = self.login_username.text()
        password = self.login_password.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return
        
        try:
            response = requests.post(
                f"{API_URL}/auth/login/",
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.login_success.emit(data['token'], data['user'])
                self.close()
            else:
                QMessageBox.warning(self, "Error", "Invalid credentials")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Login failed: {str(e)}")
    
    def handle_register(self):
        username = self.register_username.text()
        email = self.register_email.text()
        password = self.register_password.text()
        confirm = self.register_confirm.text()
        
        if not all([username, email, password, confirm]):
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
        
        try:
            response = requests.post(
                f"{API_URL}/auth/register/",
                json={"username": username, "email": email, "password": password}
            )
            
            if response.status_code == 201:
                data = response.json()
                self.login_success.emit(data['token'], data['user'])
                self.close()
            else:
                QMessageBox.warning(self, "Error", "Registration failed")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Registration failed: {str(e)}")


class DashboardTab(QWidget):
    """Dashboard showing latest dataset statistics"""
    
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Dashboard")
        refresh_btn.clicked.connect(self.load_dashboard)
        layout.addWidget(refresh_btn)
        
        # Stats layout
        self.stats_layout = QGridLayout()
        layout.addLayout(self.stats_layout)
        
        # Chart canvas
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)
        self.load_dashboard()
    
    def load_dashboard(self):
        try:
            response = requests.get(
                f"{API_URL}/datasets/",
                headers={"Authorization": f"Token {self.token}"}
            )
            
            if response.status_code == 200:
                datasets = response.json()
                if datasets:
                    self.display_stats(datasets[0])
                    self.plot_charts(datasets[0])
                else:
                    # Show message on canvas instead of popup
                    self.show_no_data_message()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load dashboard: {str(e)}")
    
    def show_no_data_message(self):
        """Display a friendly message when no data is available"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, 'No datasets uploaded yet\n\nGo to "Upload CSV" tab to upload your first dataset!',
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=16,
                transform=ax.transAxes,
                bbox=dict(boxstyle='round', facecolor='#e3f2fd', alpha=0.8))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        self.canvas.draw()
    
    def display_stats(self, dataset):
        # Clear previous stats
        for i in reversed(range(self.stats_layout.count())): 
            self.stats_layout.itemAt(i).widget().setParent(None)
        
        # Create stat cards
        stats = [
            ("Total Equipment", str(dataset['total_count']), "#3498db"),
            ("Avg Flowrate", f"{dataset['avg_flowrate']:.2f} m³/h", "#e74c3c"),
            ("Avg Pressure", f"{dataset['avg_pressure']:.2f} bar", "#2ecc71"),
            ("Avg Temperature", f"{dataset['avg_temperature']:.2f} °C", "#f39c12")
        ]
        
        for idx, (label, value, color) in enumerate(stats):
            card = QGroupBox(label)
            card.setStyleSheet(f"""
                QGroupBox {{
                    background-color: {color};
                    color: white;
                    font-weight: bold;
                    border-radius: 10px;
                    padding: 15px;
                    margin: 5px;
                }}
                QGroupBox::title {{
                    color: white;
                }}
            """)
            
            card_layout = QVBoxLayout()
            value_label = QLabel(value)
            value_label.setFont(QFont("Arial", 16, QFont.Bold))
            value_label.setStyleSheet("color: white;")
            value_label.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(value_label)
            card.setLayout(card_layout)
            
            self.stats_layout.addWidget(card, 0, idx)
    
    def plot_charts(self, dataset):
        self.figure.clear()
        
        # Create subplots
        ax1 = self.figure.add_subplot(121)
        ax2 = self.figure.add_subplot(122)
        
        # Equipment type distribution pie chart
        type_dist = dataset['type_distribution']
        ax1.pie(
            type_dist.values(),
            labels=type_dist.keys(),
            autopct='%1.1f%%',
            startangle=90,
            colors=plt.cm.Set3.colors
        )
        ax1.set_title('Equipment Type Distribution')
        
        # Average parameters bar chart
        params = ['Flowrate', 'Pressure', 'Temperature']
        values = [
            dataset['avg_flowrate'],
            dataset['avg_pressure'],
            dataset['avg_temperature']
        ]
        colors = ['#3498db', '#e74c3c', '#2ecc71']
        ax2.bar(params, values, color=colors)
        ax2.set_title('Average Parameters')
        ax2.set_ylabel('Value')
        
        self.figure.tight_layout()
        self.canvas.draw()


class UploadTab(QWidget):
    """CSV Upload Tab"""
    
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "Upload CSV File\n\n"
            "Required columns:\n"
            "• Equipment Name\n"
            "• Type\n"
            "• Flowrate\n"
            "• Pressure\n"
            "• Temperature"
        )
        instructions.setStyleSheet("""
            QLabel {
                background-color: #e3f2fd;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #2196f3;
            }
        """)
        layout.addWidget(instructions)
        
        # File selection
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        select_btn = QPushButton("Select CSV File")
        select_btn.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(select_btn)
        layout.addLayout(file_layout)
        
        # Upload button
        self.upload_btn = QPushButton("Upload")
        self.upload_btn.setEnabled(False)
        self.upload_btn.clicked.connect(self.upload_file)
        layout.addWidget(self.upload_btn)
        
        layout.addStretch()
        self.setLayout(layout)
        
        self.selected_file = None
    
    def select_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "", "CSV Files (*.csv)"
        )
        
        if filename:
            self.selected_file = filename
            self.file_label.setText(filename.split('/')[-1])
            self.upload_btn.setEnabled(True)
    
    def upload_file(self):
        if not self.selected_file:
            return
        
        try:
            with open(self.selected_file, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f"{API_URL}/datasets/upload/",
                    headers={"Authorization": f"Token {self.token}"},
                    files=files
                )
            
            if response.status_code == 201:
                QMessageBox.information(self, "Success", "File uploaded successfully!")
                self.selected_file = None
                self.file_label.setText("No file selected")
                self.upload_btn.setEnabled(False)
            else:
                QMessageBox.warning(self, "Error", f"Upload failed: {response.json().get('error', 'Unknown error')}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Upload failed: {str(e)}")


class HistoryTab(QWidget):
    """Dataset History Tab"""
    
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Refresh button
        refresh_btn = QPushButton("Refresh History")
        refresh_btn.clicked.connect(self.load_history)
        layout.addWidget(refresh_btn)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Filename', 'Upload Date', 'Count', 'Avg Flow', 'Actions'
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.load_history()
    
    def load_history(self):
        try:
            response = requests.get(
                f"{API_URL}/datasets/",
                headers={"Authorization": f"Token {self.token}"}
            )
            
            if response.status_code == 200:
                datasets = response.json()
                self.populate_table(datasets)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load history: {str(e)}")
    
    def populate_table(self, datasets):
        self.table.setRowCount(len(datasets))
        
        for row, dataset in enumerate(datasets):
            self.table.setItem(row, 0, QTableWidgetItem(str(dataset['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(dataset['filename']))
            self.table.setItem(row, 2, QTableWidgetItem(dataset['upload_date'][:19]))
            self.table.setItem(row, 3, QTableWidgetItem(str(dataset['total_count'])))
            self.table.setItem(row, 4, QTableWidgetItem(f"{dataset['avg_flowrate']:.2f}"))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            
            view_btn = QPushButton("View")
            view_btn.clicked.connect(lambda checked, d=dataset: self.view_dataset(d))
            
            pdf_btn = QPushButton("PDF")
            pdf_btn.clicked.connect(lambda checked, d=dataset: self.download_pdf(d))
            
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("background-color: #e74c3c;")
            delete_btn.clicked.connect(lambda checked, d=dataset: self.delete_dataset(d))
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(pdf_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_widget.setLayout(actions_layout)
            
            self.table.setCellWidget(row, 5, actions_widget)
    
    def view_dataset(self, dataset):
        # Show dataset details in a dialog
        dialog = DatasetDetailDialog(self.token, dataset['id'], self)
        dialog.exec_()
    
    def download_pdf(self, dataset):
        try:
            response = requests.get(
                f"{API_URL}/datasets/{dataset['id']}/report/",
                headers={"Authorization": f"Token {self.token}"}
            )
            
            if response.status_code == 200:
                filename, _ = QFileDialog.getSaveFileName(
                    self, "Save PDF", f"report_{dataset['filename']}.pdf", "PDF Files (*.pdf)"
                )
                
                if filename:
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    QMessageBox.information(self, "Success", "PDF downloaded successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download PDF: {str(e)}")
    
    def delete_dataset(self, dataset):
        reply = QMessageBox.question(
            self, 'Confirm Delete',
            f"Are you sure you want to delete {dataset['filename']}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                response = requests.delete(
                    f"{API_URL}/datasets/{dataset['id']}/delete/",
                    headers={"Authorization": f"Token {self.token}"}
                )
                
                if response.status_code == 200:
                    QMessageBox.information(self, "Success", "Dataset deleted!")
                    self.load_history()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete: {str(e)}")


class DatasetDetailDialog(QMessageBox):
    """Dialog to show dataset details"""
    
    def __init__(self, token, dataset_id, parent=None):
        super().__init__(parent)
        self.token = token
        self.dataset_id = dataset_id
        self.setWindowTitle("Dataset Details")
        self.setText("Loading...")
        self.setStandardButtons(QMessageBox.Ok)
        self.load_details()
    
    def load_details(self):
        try:
            response = requests.get(
                f"{API_URL}/datasets/{self.dataset_id}/",
                headers={"Authorization": f"Token {self.token}"}
            )
            
            if response.status_code == 200:
                dataset = response.json()
                details_text = f"""
Filename: {dataset['filename']}
Total Equipment: {dataset['total_count']}
Average Flowrate: {dataset['avg_flowrate']:.2f} m³/h
Average Pressure: {dataset['avg_pressure']:.2f} bar
Average Temperature: {dataset['avg_temperature']:.2f} °C

Equipment Types:
"""
                for eq_type, count in dataset['type_distribution'].items():
                    details_text += f"  - {eq_type}: {count}\n"
                
                self.setText(details_text)
        except Exception as e:
            self.setText(f"Error loading details: {str(e)}")


class MainWindow(QMainWindow):
    """Main Application Window"""
    
    def __init__(self, token, user):
        super().__init__()
        self.token = token
        self.user = user
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Chemical Equipment Visualizer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Header
        header = QLabel(f"Chemical Equipment Visualizer - Welcome, {self.user['username']}!")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("""
            QLabel {
                background-color: #667eea;
                color: white;
                padding: 15px;
                border-radius: 8px;
            }
        """)
        layout.addWidget(header)
        
        # Tabs
        tabs = QTabWidget()
        tabs.addTab(DashboardTab(self.token), "Dashboard")
        tabs.addTab(UploadTab(self.token), "Upload CSV")
        tabs.addTab(HistoryTab(self.token), "History")
        layout.addWidget(tabs)
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("background-color: #e74c3c;")
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)
        
        central_widget.setLayout(layout)
    
    def logout(self):
        reply = QMessageBox.question(
            self, 'Confirm Logout',
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.close()
            QApplication.quit()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    login_window = LoginWindow()

    #  Keep reference globally so it is not destroyed
    main_window_holder = {}

    def on_login_success(token, user):
        main_window_holder["window"] = MainWindow(token, user)
        main_window_holder["window"].show()

    login_window.login_success.connect(on_login_success)
    login_window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()