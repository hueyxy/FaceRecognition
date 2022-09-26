# 主程序界面
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QMdiSubWindow
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Qt
from PySide2 import QtCore

from FirstClient import Client
from SecondClient import Client2
from ThirdClient import Client3
from FourClient import Client4
from FiveClient import Client5
from lib.share import SI
import lib.dataDB as db


class Win_Main:
    def __init__(self):
        self.ui = QUiLoader().load('ui/main.ui')
        self.ui.setWindowIcon(QIcon('img/favicon.ico'))
        self.ui.move(70, 30)
        # 隐藏边框
        self.ui.setWindowFlag(QtCore.Qt.FramelessWindowHint)

        # self.ui.main.setWindowFlags(Qt.WindowCloseButtonHint)
        # 重置界面大小
        self.ui.resize(1300, 700)
        self.ui.setFixedSize(self.ui.width(), self.ui.height())
        self.ui.exit_btn.clicked.connect(self.onSignOut)

        # 定义侧边按钮点击事件
        self.ui.face_recognition_btn.clicked.connect(self.loadClient1)
        self.ui.information_input_btn.clicked.connect(self.loadClient2)
        self.ui.user_btn.clicked.connect(self.loadClient3)
        self.ui.record_btn.clicked.connect(self.loadClient4)
        self.ui.operation_btn.clicked.connect(self.loadClient5)
        self.ui.exit_btn.clicked.connect(self.onSignOut)

        self.ui.min_btn.clicked.connect(self.to_minmal)
        self.ui.close_btn.clicked.connect(self.to_close)

        self.ui.administrator.setText(SI.USER)
        self.ui.administrator.setEnabled(False)

        # 保存子窗口的字典
        self.subWinTable = {}

        print("当前用户为：", SI.USER)

    def _createSubWin(self, funcClass):
        subWinFuncObj = funcClass()
        subWindow = QMdiSubWindow()
        subWindow.setWidget(subWinFuncObj.ui)
        subWindow.setAttribute(Qt.WA_DeleteOnClose)

        self.ui.main.addSubWindow(subWindow)
        self.subWinTable[str(funcClass)] = {'subWindow': subWindow, 'subWinFuncObj': subWinFuncObj}

        # 显示子窗口
        subWindow.show()
        subWindow.setWindowState(Qt.WindowActive | Qt.WindowMaximized)

    # 子窗口
    def _loadClient(self, funcClass):
        if str(funcClass) not in self.subWinTable:
            self._createSubWin(funcClass)
            return
        # 已经创建过了直接显示子窗口
        try:
            self.subWinTable[str(funcClass)]['subWindow'].setWindowState(Qt.WindowActive | Qt.WindowMaximized)
        except:
            self._createSubWin(funcClass)

    def loadClient1(self):
        funcClass = Client
        self._loadClient(funcClass)

    def loadClient2(self):
        funcClass = Client2
        self._loadClient(funcClass)

    def loadClient3(self):
        funcClass = Client3
        self._loadClient(funcClass)

    def loadClient4(self):
        funcClass = Client4
        self._loadClient(funcClass)

    def loadClient5(self):
        funcClass = Client5
        self._loadClient(funcClass)

    # 退出
    def onSignOut(self):
        SI.USER = None
        self.ui.hide()
        SI.loginWin.ui.show()

    # 关闭窗口
    def to_close(self):
        db.closeDB()
        self.ui.close()

    # 最小化窗口
    def to_minmal(self):
        self.ui.showMinimized()


if __name__ == "__main__":
    app = QApplication([])
    SI.loginWin = Win_Main()
    SI.loginWin.ui.show()
    app.exec_()
