import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MeetingAgentApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MeetingAgentApp()
    ex.show()
    sys.exit(app.exec()) 