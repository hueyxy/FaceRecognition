# 主程序界面
import os

from PyQt5.QtCore import QSize
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QHeaderView, QTableWidgetItem
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Qt, QSize

from lib.share import SI
import lib.dataDB as db


class Client4:
    def __init__(self):
        self.ui = QUiLoader().load('ui/record.ui')
        self.ui.setWindowIcon(QIcon('img/favicon.ico'))
        self.ui.setStyleSheet("font-size: 24pt;")
        self.data = []
        COLUMN = 3
        ROW = 0
        self.ui.record_information.setColumnCount(COLUMN)
        self.ui.record_information.setRowCount(ROW)
        header_labels = ['用户名', '通行时间', '照片']
        self.ui.record_information.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.record_information.setHorizontalHeaderLabels(header_labels)
        self.ui.select_btn.clicked.connect(self.select_record_information)

    def select_record_information(self):
        username = ""
        username = self.ui.user_select.text().strip()
        if len(username) == 0:
            sql = "select * from record order by time desc "
        else:
            sql = "select * from record where username = '%s' order by time desc" % username
        self.data = db.selectDB(sql)
        self.present()

    def present(self):
        # 设置表格的行数和列数
        data_len = len(self.data)
        self.ui.record_information.setRowCount(data_len)
        self.ui.record_information.setColumnCount(3)
        self.ui.record_information.setIconSize(QSize(100, 100))
        # 在表格中添加数据
        for i in range(data_len):
            # 设置格子高度
            self.ui.record_information.setRowHeight(i, 100)
            item2 = QTableWidgetItem(self.data[i][1])
            item2.setTextAlignment(Qt.AlignCenter)
            item3 = QTableWidgetItem(str(self.data[i][2]))
            item3.setTextAlignment(Qt.AlignCenter)
            self.ui.record_information.setItem(i, 0, item2)
            self.ui.record_information.setItem(i, 1, item3)

            try:
                # 将图片加载到表格中

                item4 = QTableWidgetItem()
                item4.setFlags(Qt.ItemIsEnabled)
                item4.setIcon(QIcon(self.data[i][3]))
                self.ui.record_information.setItem(i, 2, item4)
            except Exception as e:
                print("record error:", e)

    def del_record_by_id(self, id, filePath):
        try:
            sql = "delete from  record where id = '{0}'" % id
            res = db.delDB(sql)
            if os.path.exists(filePath):
                os.remove(filePath)
                print('成功删除图片:', filePath)
            else:
                print('未找到此图片:', filePath)
            self.select_record_information()
        except Exception as e:
            print("record error:", e)


if __name__ == "__main__":
    app = QApplication([])
    SI.loginWin = Client4()
    SI.loginWin.ui.show()
    app.exec_()
