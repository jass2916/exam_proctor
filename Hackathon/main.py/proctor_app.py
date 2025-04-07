import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QStackedWidget, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage
from auth.face_auth import FaceAuthenticator
from auth.db_auth import DBAuthenticator
from proctoring.screen_monitor import ScreenMonitor
from proctoring.audio_analysis import AudioAnalyzer
from proctoring.browser_lock import BrowserLocker
from proctoring.network_monitor import NetworkMonitor
from reporting.report_generator import ReportGenerator
from reporting.database import ExamDatabase

class ExamProctorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Exam Proctor")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize components
        self.face_auth = FaceAuthenticator()
        self.db_auth = DBAuthenticator()
        self.screen_monitor = ScreenMonitor()
        self.audio_analyzer = AudioAnalyzer()
        self.browser_locker = BrowserLocker()
        self.network_monitor = NetworkMonitor()
        self.report_generator = ReportGenerator()
        self.database = ExamDatabase()
        
        # UI Setup
        self.init_ui()
        self.setup_connections()
        
        # Start background checks
        self.start_monitoring()
        
    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        
        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar_layout = QVBoxLayout()
        self.sidebar.setLayout(self.sidebar_layout)
        
        # Main content area
        self.content_area = QStackedWidget()
        
        # Add widgets to main layout
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_area)
        
        # Setup sidebar buttons
        self.setup_sidebar()
        
        # Setup pages
        self.setup_pages()
        
    def setup_sidebar(self):
        self.auth_btn = QPushButton("Authentication")
        self.monitor_btn = QPushButton("Live Monitoring")
        self.reports_btn = QPushButton("Reports")
        self.settings_btn = QPushButton("Settings")
        
        self.sidebar_layout.addWidget(self.auth_btn)
        self.sidebar_layout.addWidget(self.monitor_btn)
        self.sidebar_layout.addWidget(self.reports_btn)
        self.sidebar_layout.addWidget(self.settings_btn)
        self.sidebar_layout.addStretch()
        
    def setup_pages(self):
        # Authentication page
        self.auth_page = QWidget()
        auth_layout = QVBoxLayout()
        
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setFixedSize(640, 480)
        
        self.auth_status = QLabel("Please authenticate to begin")
        self.auth_status.setAlignment(Qt.AlignCenter)
        
        auth_layout.addWidget(self.camera_label)
        auth_layout.addWidget(self.auth_status)
        self.auth_page.setLayout(auth_layout)
        
        # Add pages to stacked widget
        self.content_area.addWidget(self.auth_page)
        # Add other pages similarly...
        
    def setup_connections(self):
        self.auth_btn.clicked.connect(lambda: self.content_area.setCurrentIndex(0))
        # Connect other buttons...
        
        # Face authentication signals
        self.face_auth.frame_ready.connect(self.update_camera_view)
        self.face_auth.auth_result.connect(self.handle_auth_result)
        
    def start_monitoring(self):
        # Start face authentication
        self.face_auth.start()
        
        # Start other monitoring services
        self.screen_monitor.start()
        self.audio_analyzer.start()
        self.browser_locker.lock_browser()
        self.network_monitor.start()
        
    def update_camera_view(self, frame):
        """Update the camera view with the latest frame"""
        image = QImage(frame, frame.shape[1], frame.shape[0], 
                      frame.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        self.camera_label.setPixmap(pixmap)
        
    def handle_auth_result(self, success, user_id):
        if success:
            self.auth_status.setText(f"Authenticated: {user_id}")
            QMessageBox.information(self, "Success", "Authentication successful!")
        else:
            self.auth_status.setText("Authentication failed")
            QMessageBox.warning(self, "Error", "Authentication failed!")
            
    def closeEvent(self, event):
        """Clean up resources when closing"""
        self.face_auth.stop()
        self.screen_monitor.stop()
        self.audio_analyzer.stop()
        self.browser_locker.unlock_browser()
        self.network_monitor.stop()
        super().closeEvent(event)