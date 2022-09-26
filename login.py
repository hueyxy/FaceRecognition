from PySide2.QtGui import QIcon, QPalette, QBrush, QPixmap
from PySide2.QtWidgets import QApplication, QMessageBox, QMdiSubWindow, QMdiArea
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QSize, Qt, QCoreApplication
from PySide2 import QtWidgets

import lib.dataDB as db
from lib.share import SI
from main import Win_Main
from register import RegisterClient
import re


# 登录
class Win_Login:
    def __init__(self):
        # 从文件加载UI定义
        self.ui = QUiLoader().load("ui/login.ui")
        self.ui.setWindowIcon(QIcon('img/favicon.ico'))
        # 设置窗口大小
        self.ui.resize(800, 450)
        # 设置窗口不可拖动
        self.ui.setFixedSize(self.ui.width(), self.ui.height())
        # 设置窗口只显示关闭按钮
        self.ui.setWindowFlags(Qt.WindowCloseButtonHint)
        # 隐藏边框
        self.ui.setWindowFlags(Qt.FramelessWindowHint)
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap("img/bg.jpg")))
        self.ui.setPalette(palette)
        # 设置关闭按钮
        # self.ui.close_btn.clicked.connect(QApplication.quit)
        self.ui.close_btn.clicked.connect(self.to_close)
        # 设置登录按钮
        self.ui.btn_login.clicked.connect(self.onSignIn)
        # 设置注册按钮
        self.ui.btn_register.clicked.connect(self.to_register)
        # 设置输入完密码后回车功能
        self.ui.edit_password.returnPressed.connect(self.onSignIn)
        # 设置最小化窗口功能
        self.ui.min_btn.clicked.connect(self.min_window)

    # 去注册页面
    def to_register(self):
        SI.registerWin = RegisterClient()
        SI.registerWin.ui.show()
        # 显示注册窗口，关闭原窗口
        self.ui.hide()

    # 最小化窗口
    def min_window(self):
        self.ui.showMinimized()

    def to_close(self):
        db.closeDB()
        print("数据库已关闭")
        self.ui.close()

    # 登录
    def onSignIn(self):
        # 获取用户名密码 去除前后误输入空格
        # username = self.ui.edit_username.text().strip()
        # ret = re.match("1[356789]\d{9}", username)
        # le = len(username)
        # # 手机号不匹配
        # if ret is None or le!=11:
        #     QMessageBox.warning(
        #         self.ui,
        #         "错误",
        #         "手机号错误"
        #     )
        #     return
        # password = self.ui.edit_password.text().strip()
        # if username == "" or password == "":
        #     QMessageBox.warning(
        #         self.ui,
        #         "错误",
        #         "用户名/密码不能为空"
        #     )
        #     return
        # sql = "select * from administrator where username = '%s' and password = '%s'" % (username, password)
        # result = db.selectDB(sql)
        # if len(result) == 0:
        #     QMessageBox.warning(
        #         self.ui,
        #         "错误",
        #         "用户名/密码错误"
        #     )
        #     return
        # SI.USER = username
        SI.mainWin = Win_Main()
        SI.mainWin.ui.show()
        # 显示登录成功后的窗口，关闭原窗口
        self.ui.hide()


app = QApplication([])
SI.loginWin = Win_Login()
SI.loginWin.ui.show()
app.exec_()
