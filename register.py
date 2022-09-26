from PySide2.QtGui import QIcon, QPalette, QBrush, QPixmap
from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QSize, Qt
from PySide2 import QtCore, QtGui, QtWidgets

import lib.dataDB as db
from lib.share import SI
from main import Win_Main
import re


# 登录
class RegisterClient:
    def __init__(self):
        # 从文件加载UI定义
        self.ui = QUiLoader().load("ui/register.ui")
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
        self.ui.close_btn.clicked.connect(QApplication.quit)
        self.ui.register_btn.clicked.connect(self.onRegisterIn)
        self.ui.min_btn.clicked.connect(self.min_window)
        self.ui.back_btn.clicked.connect(self.back_login)

    def min_window(self):
        self.ui.showMinimized()

    # 注册页面返回功能
    def back_login(self):
        self.ui.hide()
        SI.loginWin.ui.show()

    def onRegisterIn(self):
        # 获取用户名密码 去除前后误输入空格
        username = self.ui.register_username.text().strip()
        password = self.ui.register_password.text().strip()
        ack_psd = self.ui.again_password.text().strip()
        # 匹配手机号
        ret = re.match("1[356789]\d{9}", username)
        le = len(username)
        # 手机号不匹配
        if ret is None or le != 11:
            QMessageBox.warning(
                self.ui,
                "错误",
                "手机号错误"
            )
            return
        # 匹配密码包含数字，字母，特殊字符
        ret_psd = re.match(
            "^(?![A-Za-z]+$)(?![A-Z0-9]+$)(?![a-z0-9]+$)(?![a-z\W]+$)(?![A-Z\W]+$)(?![0-9\W]+$)[a-zA-Z0-9\W]{8,16}$",
            password)
        if not ret_psd:
            QMessageBox.warning(
                self.ui,
                "错误",
                "密码不符合要求，必须包含字母、数字、特殊字符"
            )
            return

        if len(username) == 0 or len(password) == 0 or len(ack_psd) == 0:
            QMessageBox.warning(
                self.ui,
                "错误",
                "用户名/密码不能为空"
            )
            return
        if str(password) != str(ack_psd):
            QMessageBox.warning(
                self.ui,
                "错误",
                "两次输入密码不一致"
            )
            return
        sql = "select * from administrator where username = '%s'" % username
        result = db.selectDB(sql)
        if len(result) != 0:
            QMessageBox.warning(
                self.ui,
                "错误",
                "该账号已存在，请重新注册"
            )
            return
        else:

            sql2 = "insert into administrator(username,password) values ('%s','%s')" % (username, password)
            res = db.insertDB(sql2)
            # 添加自定义弹窗
            SMBox = QMessageBox(QMessageBox.Information, '注册成功', '恭喜您注册成功')
            pix_img = QtGui.QPixmap('img/success2.png')
            pix_img = pix_img.scaled(25, 25, QtCore.Qt.KeepAspectRatio)
            SMBox.setIconPixmap(QPixmap(pix_img))
            SMBox.setText("恭喜您注册成功")
            agreeBtn = SMBox.addButton("确认", QMessageBox.AcceptRole)
            SMBox.exec()
            if SMBox.clickedButton() == agreeBtn:
                SI.USER = username
                SI.mainWin = Win_Main()
                SI.mainWin.ui.show()
                # 显示登录成功后的窗口，关闭原窗口
                self.ui.hide()


if __name__ == "__main__":
    app = QApplication([])
    SI.loginWin = RegisterClient()
    SI.loginWin.ui.show()
    app.exec_()
