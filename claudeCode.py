import sys
import os
import csv
import subprocess
import time
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QComboBox, QTreeWidget, QTreeWidgetItem, QSplitter,
                            QTextEdit, QMessageBox, QMenuBar, QMenu, QAction,
                            QGridLayout, QFrame)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QFont, QPainter

# Worker thread for background operations
class CommandWorker(QThread):
    output_signal = pyqtSignal(str)
    
    def __init__(self, commands):
        super().__init__()
        self.commands = commands
    
    def run(self):
        for command in self.commands:
            try:
                if command['type'] == 'ping':
                    self.output_signal.emit(f"Executing: {command['cmd']}\n")
                    result = subprocess.run(command['cmd'], shell=True, capture_output=True, text=True)
                    self.output_signal.emit(f"Result: {result.stdout}\n")
                elif command['type'] == 'bash':
                    self.output_signal.emit(f"Running bash file: {command['file']}\n")
                    if os.path.exists(command['file']):
                        result = subprocess.run(['bash', command['file']], capture_output=True, text=True)
                        self.output_signal.emit(f"Bash output: {result.stdout}\n")
                    else:
                        self.output_signal.emit(f"Bash file not found: {command['file']}\n")
                elif command['type'] == 'sleep':
                    time.sleep(command['duration'])
                    self.output_signal.emit(f"Slept for {command['duration']} seconds\n")
            except Exception as e:
                self.output_signal.emit(f"Error: {str(e)}\n")

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Login Page')
        self.setFixedSize(400, 450)
        
        # Set background image
        self.set_background_image('login_bg.jpg')
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(50, 50, 50, 50)
        
        # Create semi-transparent widget for better visibility
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 220);
                border-radius: 10px;
                padding: 20px;
            }
        """)
        container_layout = QVBoxLayout()
        
        # Login Label
        login_label = QLabel('Log In')
        login_label.setAlignment(Qt.AlignCenter)
        login_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333;
                padding: 10px;
            }
        """)
        container_layout.addWidget(login_label)
        
        # Username field
        username_layout = QHBoxLayout()
        username_label = QLabel('Username:')
        username_label.setFixedWidth(80)
        self.username_combo = QComboBox()
        self.username_combo.addItems(['user1', 'user2', 'user3'])
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_combo)
        container_layout.addLayout(username_layout)
        
        # Password field
        password_layout = QHBoxLayout()
        password_label = QLabel('Password:')
        password_label.setFixedWidth(80)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        container_layout.addLayout(password_layout)
        
        # Plane field
        plane_layout = QHBoxLayout()
        plane_label = QLabel('Plane:')
        plane_label.setFixedWidth(80)
        self.plane_combo = QComboBox()
        self.plane_combo.addItems(['plane1', 'plane2', 'plane3'])
        plane_layout.addWidget(plane_label)
        plane_layout.addWidget(self.plane_combo)
        container_layout.addLayout(plane_layout)
        
        # LRU1 and LRU2 fields
        lru_layout = QHBoxLayout()
        lru1_label = QLabel('LRU1:')
        self.lru1_input = QLineEdit('1')
        lru2_label = QLabel('LRU2:')
        self.lru2_input = QLineEdit('1')
        lru_layout.addWidget(lru1_label)
        lru_layout.addWidget(self.lru1_input)
        lru_layout.addWidget(lru2_label)
        lru_layout.addWidget(self.lru2_input)
        container_layout.addLayout(lru_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.login_button = QPushButton('Login')
        self.reset_button = QPushButton('Reset Fields')
        self.login_button.clicked.connect(self.login)
        self.reset_button.clicked.connect(self.reset_fields)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.reset_button)
        container_layout.addLayout(button_layout)
        
        container.setLayout(container_layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        
    def set_background_image(self, image_path):
        if not os.path.exists(image_path):
            # Create a default background if image doesn't exist
            self.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #667eea, stop:1 #764ba2);
                }
            """)
        else:
            palette = QPalette()
            pixmap = QPixmap(image_path)
            palette.setBrush(QPalette.Background, QBrush(pixmap))
            self.setPalette(palette)
    
    def login(self):
        username = self.username_combo.currentText()
        password = self.password_input.text()
        plane = self.plane_combo.currentText()
        lru1 = self.lru1_input.text()
        lru2 = self.lru2_input.text()
        
        # Validate credentials
        valid_credentials = {
            'user1': {'password': 'pass1', 'plane': 'plane1'},
            'user2': {'password': 'pass2', 'plane': 'plane2'},
            'user3': {'password': 'pass3', 'plane': 'plane3'}
        }
        
        if (username in valid_credentials and 
            password == valid_credentials[username]['password'] and 
            plane == valid_credentials[username]['plane'] and
            lru1 == '1' and lru2 == '1'):
            
            # Log the login details
            self.log_login(username, plane, lru1, lru2)
            
            # Run initial bash and ping commands
            self.run_login_commands(username)
            
            # Open main window
            self.main_window = MainWindow(username)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, 'Login Failed', 'Invalid credentials!')
    
    def reset_fields(self):
        self.username_combo.setCurrentIndex(0)
        self.password_input.clear()
        self.plane_combo.setCurrentIndex(0)
        self.lru1_input.setText('1')
        self.lru2_input.setText('1')
    
    def log_login(self, username, plane, lru1, lru2):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_data = [timestamp, username, plane, lru1, lru2, 'Login Successful']
        
        file_exists = os.path.exists('logfile.csv')
        with open('logfile.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(['Timestamp', 'Username', 'Plane', 'LRU1', 'LRU2', 'Status'])
            writer.writerow(log_data)
    
    def run_login_commands(self, username):
        # Create dummy bash files if they don't exist
        bash_files = {
            'user1': 'user1_login.sh',
            'user2': 'user2_login.sh',
            'user3': 'user3_login.sh'
        }
        
        bash_file = bash_files[username]
        if not os.path.exists(bash_file):
            with open(bash_file, 'w') as f:
                f.write(f'#!/bin/bash\necho "Login script for {username}"\ndate\n')
        
        # Run ping command (dummy)
        ping_commands = {
            'user1': 'ping -n 1 8.8.8.8',
            'user2': 'ping -n 1 1.1.1.1',
            'user3': 'ping -n 1 4.4.4.4'
        }
        
        try:
            subprocess.run(ping_commands[username], shell=True, capture_output=True)
        except:
            pass

class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(f'Main Application - {self.username}')
        self.setGeometry(100, 100, 1200, 800)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal layout
        main_layout = QHBoxLayout()
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Tree widget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel('Navigation Tree')
        self.create_tree_structure()
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)
        
        # Right side - Split into upper and lower
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        # Upper part - Image with version and username
        upper_widget = QWidget()
        upper_widget.setMinimumHeight(200)
        upper_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 10px;
            }
        """)
        
        # Create labels for version and username
        upper_layout = QGridLayout()
        
        username_label = QLabel(f'User: {self.username}')
        username_label.setStyleSheet('color: white; font-size: 14px; font-weight: bold;')
        username_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        
        version_label = QLabel('Version: 1.0.0')
        version_label.setStyleSheet('color: white; font-size: 14px; font-weight: bold;')
        version_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        
        upper_layout.addWidget(username_label, 1, 0, Qt.AlignLeft | Qt.AlignBottom)
        upper_layout.addWidget(version_label, 1, 1, Qt.AlignRight | Qt.AlignBottom)
        upper_widget.setLayout(upper_layout)
        
        # Lower part - Output display
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.output_display.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #00ff00;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        
        right_layout.addWidget(upper_widget, 1)
        right_layout.addWidget(self.output_display, 3)
        right_widget.setLayout(right_layout)
        
        # Add to splitter
        splitter.addWidget(self.tree_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 800])
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        file_action = QAction('Open', self)
        file_action.triggered.connect(lambda: QMessageBox.information(self, 'File', 'File menu clicked'))
        file_menu.addAction(file_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        view_action = QAction('Refresh', self)
        view_action.triggered.connect(lambda: QMessageBox.information(self, 'View', 'View menu clicked'))
        view_menu.addAction(view_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        help_action = QAction('About', self)
        help_action.triggered.connect(lambda: QMessageBox.information(self, 'Help', 'Help menu clicked'))
        help_menu.addAction(help_action)
        
        # Settings menu
        settings_menu = menubar.addMenu('Settings')
        settings_action = QAction('Preferences', self)
        settings_action.triggered.connect(lambda: QMessageBox.information(self, 'Settings', 'Settings menu clicked'))
        settings_menu.addAction(settings_action)
        
        # Logout menu
        logout_menu = menubar.addMenu('Logout')
        logout_action = QAction('Logout', self)
        logout_action.triggered.connect(self.logout)
        logout_menu.addAction(logout_action)
    
    def create_tree_structure(self):
        # Create different tree structures based on username
        if self.username == 'user1':
            self.create_user1_tree()
        elif self.username == 'user2':
            self.create_user2_tree()
        else:
            self.create_user3_tree()
    
    def create_user1_tree(self):
        root = QTreeWidgetItem(self.tree_widget, ['Main Node User1'])
        
        # Node 1 with complex structure
        node1 = QTreeWidgetItem(root, ['Node 1'])
        node1_1 = QTreeWidgetItem(node1, ['Node 1.1'])
        node1_1_1 = QTreeWidgetItem(node1_1, ['Node 1.1.1'])
        node1_1_2 = QTreeWidgetItem(node1_1, ['Node 1.1.2'])
        node1_1_3 = QTreeWidgetItem(node1_1, ['Node 1.1.3'])
        node1_1_3_1 = QTreeWidgetItem(node1_1_3, ['Node 1.1.3.1'])
        node1_1_3_1_1 = QTreeWidgetItem(node1_1_3_1, ['Node 1.1.3.1.1'])
        node1_1_3_1_2 = QTreeWidgetItem(node1_1_3_1, ['Node 1.1.3.1.2'])
        node1_1_3_1_3 = QTreeWidgetItem(node1_1_3_1, ['Node 1.1.3.1.3'])
        node1_1_3_1_4 = QTreeWidgetItem(node1_1_3_1, ['Node 1.1.3.1.4'])
        node1_1_3_2 = QTreeWidgetItem(node1_1_3, ['Node 1.1.3.2'])
        node1_2 = QTreeWidgetItem(node1, ['Node 1.2'])
        
        # Node 2
        node2 = QTreeWidgetItem(root, ['Node 2'])
        node2_1 = QTreeWidgetItem(node2, ['Node 2.1'])
        
        # Node 3
        node3 = QTreeWidgetItem(root, ['Node 3'])
        node3_1 = QTreeWidgetItem(node3, ['Node 3.1'])
        node3_2 = QTreeWidgetItem(node3, ['Node 3.2'])
        node3_3 = QTreeWidgetItem(node3, ['Node 3.3'])
        node3_4 = QTreeWidgetItem(node3, ['Node 3.4'])
        
        # Node 4
        node4 = QTreeWidgetItem(root, ['Node 4'])
        node4_1 = QTreeWidgetItem(node4, ['Node 4.1'])
        
        # Node 5
        node5 = QTreeWidgetItem(root, ['Node 5'])
        for i in range(1, 6):
            QTreeWidgetItem(node5, [f'Node 5.{i}'])
        
        # Node 6
        node6 = QTreeWidgetItem(root, ['Node 6'])
        node6_1 = QTreeWidgetItem(node6, ['Node 6.1'])
        node6_2 = QTreeWidgetItem(node6, ['Node 6.2'])
        node6_3 = QTreeWidgetItem(node6, ['Node 6.3'])
        node6_3_1 = QTreeWidgetItem(node6_3, ['Node 6.3.1'])
        node6_3_2 = QTreeWidgetItem(node6_3, ['Node 6.3.2'])
        node6_3_3 = QTreeWidgetItem(node6_3, ['Node 6.3.3'])
        
        # Nodes 7-11
        node7 = QTreeWidgetItem(root, ['Node 7'])
        node7_1 = QTreeWidgetItem(node7, ['Node 7.1'])
        node7_2 = QTreeWidgetItem(node7, ['Node 7.2'])
        
        node8 = QTreeWidgetItem(root, ['Node 8'])
        node8_1 = QTreeWidgetItem(node8, ['Node 8.1'])
        node8_2 = QTreeWidgetItem(node8, ['Node 8.2'])
        
        node9 = QTreeWidgetItem(root, ['Node 9'])
        node9_1 = QTreeWidgetItem(node9, ['Node 9.1'])
        
        node10 = QTreeWidgetItem(root, ['Node 10'])
        node10_1 = QTreeWidgetItem(node10, ['Node 10.1'])
        
        node11 = QTreeWidgetItem(root, ['Node 11'])
        node11_1 = QTreeWidgetItem(node11, ['Node 11.1'])
        
        # Leaf nodes 12 and 13
        node12 = QTreeWidgetItem(root, ['Node 12 (Leaf)'])
        node13 = QTreeWidgetItem(root, ['Node 13 (Leaf)'])
    
    def create_user2_tree(self):
        root = QTreeWidgetItem(self.tree_widget, ['Main Node User2'])
        
        # Simplified structure for user2
        for i in range(1, 14):
            node = QTreeWidgetItem(root, [f'User2 Node {i}'])
            if i <= 5:
                for j in range(1, 4):
                    QTreeWidgetItem(node, [f'User2 Node {i}.{j}'])
    
    def create_user3_tree(self):
        root = QTreeWidgetItem(self.tree_widget, ['Main Node User3'])
        
        # Different structure for user3
        for i in range(1, 14):
            node = QTreeWidgetItem(root, [f'User3 Node {i}'])
            if i % 2 == 0:
                for j in range(1, 3):
                    subnode = QTreeWidgetItem(node, [f'User3 Node {i}.{j}'])
                    if i == 4:
                        for k in range(1, 3):
                            QTreeWidgetItem(subnode, [f'User3 Node {i}.{j}.{k}'])
    
    def on_tree_item_clicked(self, item, column):
        node_name = item.text(0)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Check if it's a leaf node (no children)
        is_leaf = item.childCount() == 0
        
        self.output_display.append(f"\n[{timestamp}] Clicked: {node_name}")
        
        if is_leaf:
            self.handle_leaf_node_click(node_name)
        else:
            self.handle_non_leaf_node_click(node_name)
    
    def handle_leaf_node_click(self, node_name):
        self.output_display.append(f"Executing leaf node operations for: {node_name}\n")
        
        # 1. Ping check
        ping_cmd = f"ping -n 1 8.8.8.8"
        try:
            result = subprocess.run(ping_cmd, shell=True, capture_output=True, text=True, timeout=5)
            self.output_display.append(f"Ping result: {result.stdout[:200]}...\n")
        except Exception as e:
            self.output_display.append(f"Ping error: {str(e)}\n")
        
        # 2. Read file
        try:
            if not os.path.exists('input.txt'):
                with open('input.txt', 'w') as f:
                    f.write('Sample input file content for testing.')
            
            with open('input.txt', 'r') as f:
                content = f.read()
                self.output_display.append(f"File content: {content}\n")
        except Exception as e:
            self.output_display.append(f"Read file error: {str(e)}\n")
        
        # 3. User-defined function call
        self.user_defined_function(node_name, self.username)
        
        # 4. Append to log file
        self.append_to_event_log('leaf_events.csv', node_name, 'Leaf node clicked')
        
        # 5. Write text to file
        try:
            with open('output.txt', 'w') as f:
                f.write('Hello World')
            self.output_display.append("Written 'Hello World' to output.txt\n")
        except Exception as e:
            self.output_display.append(f"Write file error: {str(e)}\n")
        
        # 6. Check if file exists
        if os.path.exists('output.txt'):
            self.output_display.append("output.txt exists\n")
        else:
            self.output_display.append("output.txt does not exist\n")
        
        # 7. Show message box
        QMessageBox.information(self, 'Info', 'Process Running')
        
        # 8. Sleep for 2 seconds
        self.output_display.append("Sleeping for 2 seconds...\n")
        QApplication.processEvents()
        time.sleep(2)
        self.output_display.append("Sleep completed\n")
        
        # 9. Delete temp file
        try:
            if os.path.exists('temp.txt'):
                os.remove('temp.txt')
                self.output_display.append("temp.txt deleted\n")
            else:
                self.output_display.append("temp.txt does not exist\n")
        except Exception as e:
            self.output_display.append(f"Delete file error: {str(e)}\n")
        
        # 10. Get hex files in directory
        hex_files = [f for f in os.listdir('.') if f.endswith('.hex')]
        self.output_display.append(f"Hex files found: {hex_files}\n")
        
        # 11. Collapse TreeView
        self.tree_widget.collapseAll()
        self.output_display.append("Tree view collapsed\n")
    
    def handle_non_leaf_node_click(self, node_name):
        self.output_display.append(f"Executing non-leaf node operations for: {node_name}\n")
        
        # Run ping command
        ping_cmd = f"ping -n 1 1.1.1.1"
        try:
            result = subprocess.run(ping_cmd, shell=True, capture_output=True, text=True, timeout=5)
            self.output_display.append(f"Connection ping result: Success\n")
        except Exception as e:
            self.output_display.append(f"Connection ping error: {str(e)}\n")
        
        # Run bash file
        bash_file = f"{self.username}_{node_name.replace(' ', '_')}.sh"
        if not os.path.exists(bash_file):
            with open(bash_file, 'w') as f:
                f.write(f'#!/bin/bash\necho "Bash script for {node_name}"\ndate\n')
        
        try:
            if sys.platform == 'win32':
                # For Windows, try to run with Git Bash or WSL if available
                self.output_display.append(f"Bash file {bash_file} created (Windows environment)\n")
            else:
                result = subprocess.run(['bash', bash_file], capture_output=True, text=True)
                self.output_display.append(f"Bash output: {result.stdout}\n")
        except Exception as e:
            self.output_display.append(f"Bash execution info: {str(e)}\n")
        
        # Log to non-leaf events
        self.append_to_event_log('non_leaf_events.csv', node_name, 'Non-leaf node clicked')
    
    def user_defined_function(self, node_name, username):
        self.output_display.append(f"User-defined function called with args: {node_name}, {username}\n")
        # Add custom logic here
        return f"Processed {node_name} for {username}"
    
    def append_to_event_log(self, filename, node_name, event_type):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        event_data = [timestamp, self.username, node_name, event_type]
        
        file_exists = os.path.exists(filename)
        try:
            with open(filename, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists:
                    writer.writerow(['Timestamp', 'Username', 'Node', 'Event'])
                writer.writerow(event_data)
            self.output_display.append(f"Event logged to {filename}\n")
        except Exception as e:
            self.output_display.append(f"Error logging event: {str(e)}\n")
    
    def logout(self):
        reply = QMessageBox.question(self, 'Logout', 'Are you sure you want to logout?',
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Save any pending data
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open('logfile.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([timestamp, self.username, '', '', '', 'Logout'])
            
            # Return to login window
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create initial input.txt if it doesn't exist
    if not os.path.exists('input.txt'):
        with open('input.txt', 'w') as f:
            f.write('This is a sample input file.\nIt contains multiple lines.\nFor testing purposes.')
    
    # Start with login window
    login_window = LoginWindow()
    login_window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()