from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication
from PySide2.QtUiTools import QUiLoader
from lib.share import SI


class Client5:
    def __init__(self):
        self.current_face_position = []
        self.ui = QUiLoader().load('ui/operation.ui')
        self.ui.setWindowIcon(QIcon('img/favicon.ico'))


if __name__ == "__main__":
    app = QApplication([])
    SI.loginWin = Client5()
    SI.loginWin.ui.show()
    app.exec_()
