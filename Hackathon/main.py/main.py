import sys
from PyQt5.QtWidgets import QApplication
from proctor_app import ExamProctorApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExamProctorApp()
    window.show()
    sys.exit(app.exec_())