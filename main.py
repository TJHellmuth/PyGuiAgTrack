import fontend
import logic
import sys

from PyQt6.QtWidgets import QApplication


if __name__ == "__main__":
    log = logic.logic(sys.argv)
    app = QApplication([])
    app.setStyleSheet("QWidget{font-size:20px;}");

    window = fontend.Window(log)
    window.show()

    sys.exit(app.exec())


