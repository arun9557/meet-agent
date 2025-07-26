import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QTextEdit, QGridLayout, QListWidget, QListWidgetItem,
                             QFileDialog)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap

from google_services.meeting_logic import fetch_upcoming_events, transcribe_audio
from ai_agent.agent import generate_summary, extract_key_takeaways
from database import create_connection, add_meeting
import datetime

MODERN_STYLE_SHEET = """
    QWidget#MainWindow {
        background-color: #FFFFFF;
        font-family: "Inter", sans-serif;
    }
    /* Header */
    QWidget#Header {
        background-color: #3D4A5C;
        color: #FFFFFF;
        padding: 20px;
        border-radius: 15px;
    }
    QLabel#TimeLabel {
        font-size: 48px;
        font-weight: bold;
    }
    QLabel#DateLabel {
        font-size: 18px;
    }
    /* Right Sidebar */
    QWidget#RightSidebar {
        background-color: #FFFFFF;
        border-left: none;
    }
    QLabel#MeetingsHeader {
        font-size: 16px;
        font-weight: bold;
        padding: 20px 20px 10px 20px;
        color: #333333;
    }
    QListWidget {
        border: none;
        background-color: #FFFFFF;
    }
    QListWidget::item {
        border-radius: 10px;
        background-color: #F8F9FA;
        margin: 5px 20px;
        padding: 15px;
        border: 1px solid #E9ECEF;
    }
    /* Controls */
    QWidget#Controls {
        padding: 10px 20px;
    }
    QPushButton {
        background-color: transparent;
        border: none;
        font-size: 18px;
        color: #555;
    }
    QPushButton#TodayButton {
        font-weight: bold;
        color: #000;
        border: 1px solid #DEE2E6;
        border-radius: 5px;
        padding: 5px 10px;
    }
"""

class MeetingAgentApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.setWindowTitle('Meeting Agent')
        self.setMinimumSize(960, 600)
        self.initUI()
        self.setStyleSheet(MODERN_STYLE_SHEET)
        self.load_upcoming_meetings()

    def initUI(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Main content area (Left)
        main_content = QWidget()
        main_content_layout = QVBoxLayout(main_content)
        main_content_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QWidget()
        header.setObjectName("Header")
        header_layout = QHBoxLayout(header)

        # Plant icon
        plant_icon = QLabel()
        plant_pixmap = QPixmap("plant_icon.png").scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        plant_icon.setPixmap(plant_pixmap)

        time_date_layout = QVBoxLayout()
        self.time_label = QLabel()
        self.time_label.setObjectName("TimeLabel")
        self.date_label = QLabel()
        self.date_label.setObjectName("DateLabel")
        time_date_layout.addWidget(self.time_label)
        time_date_layout.addWidget(self.date_label)

        header_layout.addWidget(plant_icon)
        header_layout.addLayout(time_date_layout)
        header_layout.addStretch()

        # Timer to update time
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        self.update_time()

        # Process Meeting Button
        self.process_meeting_button = QPushButton("Process a Past Meeting")
        self.process_meeting_button.clicked.connect(self.process_meeting)

        main_content_layout.addWidget(header)
        main_content_layout.addWidget(self.process_meeting_button)
        main_content_layout.addStretch()

        # Right Sidebar for meetings
        right_sidebar = QWidget()
        right_sidebar.setObjectName("RightSidebar")
        right_sidebar.setFixedWidth(320)
        sidebar_layout = QVBoxLayout(right_sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Controls
        controls_widget = QWidget()
        controls_widget.setObjectName("Controls")
        controls_layout = QHBoxLayout(controls_widget)
        
        today_button = QPushButton("Today")
        today_button.setObjectName("TodayButton")
        prev_button = QPushButton("<")
        next_button = QPushButton(">")
        more_button = QPushButton("...")
        add_button = QPushButton("+")

        controls_layout.addWidget(today_button)
        controls_layout.addWidget(prev_button)
        controls_layout.addWidget(next_button)
        controls_layout.addStretch()
        controls_layout.addWidget(more_button)
        controls_layout.addWidget(add_button)
        
        self.meetings_list = QListWidget()
        self.meetings_list.setSpacing(5)

        sidebar_layout.addWidget(controls_widget)
        sidebar_layout.addWidget(self.meetings_list)

        main_layout.addWidget(main_content)
        main_layout.addWidget(right_sidebar)
        
        self.setLayout(main_layout)

    def process_meeting(self):
        """Handles the AI processing of a selected meeting audio file."""
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            "Select Meeting Audio File",
            "",
            "Audio Files (*.wav *.mp3)"
        )
        if fileName:
            print(f"Selected file: {fileName}")
            # Here we will call the AI processing functions
            # and save the results to the database.
            self.run_ai_processing(fileName)

    def run_ai_processing(self, audio_file):
        """Coordinates the AI processing and database storage."""
        print("Starting AI processing...")
        
        transcript = transcribe_audio(audio_file)
        if "Error" in transcript:
            print(transcript)
            return
        
        ai_summary = generate_summary(transcript)
        if "Error" in ai_summary:
            print(ai_summary)
            return

        key_takeaways = extract_key_takeaways(transcript)
        if "Error" in key_takeaways:
            print(key_takeaways)
            return

        conn = create_connection()
        if conn:
            meeting_data = (
                datetime.datetime.now().isoformat(),
                "Processed Meeting", # Placeholder for summary
                transcript,
                ai_summary,
                key_takeaways
            )
            add_meeting(conn, meeting_data)
            conn.close()
            print("Meeting processed and saved to database.")

    def update_time(self):
        from datetime import datetime
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M"))
        self.date_label.setText(now.strftime("%A, %B %d"))

    def load_upcoming_meetings(self):
        events = fetch_upcoming_events(10) 
        self.meetings_list.clear()
        
        if not events:
            no_meetings_item = QListWidgetItem("No upcoming meetings found.")
            self.meetings_list.addItem(no_meetings_item)
            return

        for event in events:
            summary = event.get('summary', 'No Title')
            start_time_iso = event.get('start', {}).get('dateTime', '')
            
            item_widget = QWidget()
            item_layout = QVBoxLayout(item_widget)
            item_layout.setSpacing(5)
            
            summary_label = QLabel(summary)
            summary_label.setFont(QFont("Inter", 10, QFont.Weight.Bold))
            summary_label.setWordWrap(True)
            
            from datetime import datetime
            time_text = "All day"
            if start_time_iso:
                dt_object = datetime.fromisoformat(start_time_iso.replace('Z', '+00:00'))
                time_text = dt_object.strftime('%H:%M')

            time_label = QLabel(time_text)
            time_label.setFont(QFont("Inter", 9))
            time_label.setStyleSheet("color: #555555;")
            
            item_layout.addWidget(summary_label)
            item_layout.addWidget(time_label)

            # Placeholder for host info if available
            host_label = QLabel("Host: Arun Pratap Singh (B24BS2044)")
            host_label.setFont(QFont("Inter", 9))
            host_label.setStyleSheet("color: #555555;")
            item_layout.addWidget(host_label)
            
            list_item = QListWidgetItem(self.meetings_list)
            list_item.setSizeHint(item_widget.sizeHint())
            self.meetings_list.addItem(list_item)
            self.meetings_list.setItemWidget(list_item, item_widget) 