# 已录入员工信息展示，批量导入
import datetime
import os
import time

import cv2
import dlib
import xlrd
from PyQt5.QtCore import QSize
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QFormLayout, QMessageBox, QMdiSubWindow, QHeaderView, QTableWidgetItem, \
    QFileDialog, QTableWidget, QDialog
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Qt, QSize
from PySide2 import QtWidgets

from lib.share import SI
import lib.share as sa
import lib.dataDB as db
import traceback
from add_dialog import AddDialog
import re as ze


class Client3:
    def __init__(self):
        self.ui = QUiLoader().load('ui/all_user_information.ui')
        self.ui.setWindowIcon(QIcon('img/favicon.ico'))
        self.ui.progressBar.setValue(0)
        self.ui.setStyleSheet("font-size: 22pt;")
        self.data = []
        COLUMN = 4
        ROW = 0
        self.ui.all_user_table.setColumnCount(COLUMN)
        self.ui.all_user_table.setRowCount(ROW)
        # 设置表头
        header_labels = ['用户ID', '用户名', '不戴口罩照片', '戴口罩照片']
        self.ui.all_user_table.setHorizontalHeaderLabels(header_labels)
        # self.ui.all_user_table.verticalHeader().setVisible(False)
        self.ui.all_user_table.setShowGrid(True)
        self.ui.all_user_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.ui.all_user_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.ui.all_user_table.setSelectionMode(QTableWidget.SingleSelection)
        self.ui.all_user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # for index in range(self.ui.all_user_table.columnCount()):
        #     headItem = self.ui.all_user_table.horizontalHeaderItem(index)
        #     headItem.setTextAlignment(Qt.AlignVCenter)

        self.ui.input_pic.clicked.connect(self.input_pic_from_root)
        self.ui.input_excel.clicked.connect(self.input_excel_from_root)

        self.ui.select_btn.clicked.connect(self.select_user_infor_from_data)
        self.ui.del_btn.clicked.connect(self.del_data_row)
        self.ui.add_btn.clicked.connect(self.add_btn_click)

    def input_pic_from_root(self):
        try:
            # 重置进度条
            self.ui.progressBar.reset()
            filePath = QFileDialog.getExistingDirectory(self.ui, "选择图片路径")
            if not filePath:
                return
            # 设置项目根目录
            SI.projectPath = filePath
            fileList = []
            for root, dirs, files in os.walk(filePath):
                fileList = files
            # 获取图片路径
            self.ui.progressBar.setRange(0, len(fileList))
            count = 1
            for flist in fileList:
                self.ui.progressBar.setValue(count)
                count += 1
                # 完整路径
                new_file = filePath + "/" + flist
                img = cv2.imread(new_file)
                print("new_file", new_file)
                ############################################
                ## 获取图片完整路径后，先判断图片是否已经存在
                # 获取员工号
                uid = flist.split('_')[0]
                ret = ze.match("\d{12}", uid)
                uid_len = len(uid)
                # 判断照片命名是否合法
                if ret is None or uid_len != 12:
                    QMessageBox.warning(
                        self.ui,
                        'warning',
                        '照片命名不合法1')
                    # 重置进度条
                    self.ui.progressBar.reset()
                    return
                mask = flist.split('_')[1]
                print("mask:", mask)
                if str(mask) != "mask.jpg" and str(mask) != "nomask.jpg":
                    QMessageBox.warning(
                        self.ui,
                        'warning',
                        '照片命名不合法2')
                    # 重置进度条
                    self.ui.progressBar.reset()
                    return
                # 是否佩戴口罩
                print("uid = {0},mask = {1}".format(uid, mask))
                # 默认不戴口罩
                flag = 0
                if mask == "mask.jpg":
                    flag = 1
                # 判断员工号某类照片是否存在，存在更新，不存在插入信息
                new_File_Path = "user_img/" + flist
                print("flag:", flag)
                print("new_file_path:", new_File_Path)
                t1 = time.time()
                s1 = "select * from picture where uid = '{0}'".format(uid)
                res = db.selectDB(s1)
                # 不存在
                s2 = ""
                if len(res) == 0:
                    # 不戴口罩
                    if flag == 0:
                        s2 = "insert into picture(uid,nomask_path) values('{0}','{1}') ".format(uid, new_File_Path)
                    else:
                        s2 = "insert into picture(uid,mask_path) values('{0}','{1}') ".format(uid, new_File_Path)
                else:
                    # 不戴口罩
                    if flag == 0:
                        s2 = "update picture set nomask_path = '{0}' where uid = '{1}'".format(new_File_Path, uid)
                    else:
                        s2 = "update picture set mask_path = '{0}' where uid = '{1}'".format(new_File_Path, uid)
                print(s2)
                res2 = db.insertDB(s2)
                print("res:", res2)
                t2 = time.time()
                print("插入图片运行时间：", str(t2 - t1))

                # 处理源文件和镜像文件的函数
                # img, fa, fa_mi = sa.process_pic_from_root(img)
                img, fa = sa.process_pic_from_root(img)
                # sql2 = "insert into features(uid,mirror,mask,featureX) values ('%s',%d,%d,'%s'),('%s',%d,%d,'%s')" % (
                #     uid, 0, flag, fa, uid, 1, flag, fa_mi)
                sql2 = "insert into features(uid,mirror,mask,featureX) values ('%s',%d,%d,'%s')" % (uid, 0, flag, fa)
                result2 = db.insertDB(sql2)
                print("插入特征值：", result2)
                cv2.imencode('.jpg', img)[1].tofile(new_File_Path)
            QMessageBox.information(self.ui, "成功", "导入成功")
            sql = "select * from user left join picture on user.uid = picture.uid"
            self.data = sa.get_all_user_information(sql)
            self.present()
            self.ui.progressBar.setValue(0)
        except Exception as e:
            traceback.print_exc()
            QMessageBox.warning(
                self.ui,
                '错误',
                str(e)
            )

    def input_excel_from_root(self):
        try:
            # 重置进度条
            self.ui.progressBar.reset()
            filePath, _ = QFileDialog.getOpenFileName(
                self.ui,  # 父窗口对象
                "选择你要上传的excel文件",  # 标题
                r"E:\\",  # 起始目录
                'Excel files(*.xlsx , *.xls)'  # 选择类型过滤项，过滤内容在括号中
            )
            if not filePath:
                return
            print(filePath)
            xl = xlrd.open_workbook(filePath)
            tables = xl.sheets()[0]
            rows = tables.nrows
            data = []
            for i in range(1, rows):
                data.append(tables.row_values(i))

            print("导入数据", data)
            # 获取系统当前时间
            curr_time = datetime.datetime.now()
            curTime = datetime.datetime.strftime(curr_time, '%Y-%m-%d %H:%M:%S')
            print("beginTime:", curTime)
            self.ui.progressBar.setRange(0, len(data))
            count = 1
            for i in data:
                self.ui.progressBar.setValue(count)
                count += 1
                ret = ze.match("\d{12}", i[0])
                uid_len = len(i[0])
                # 判断照片命名是否合法
                if ret is None or uid_len != 12:
                    QMessageBox.warning(
                        self.ui,
                        'warning',
                        '工号不合法，请检查并修改')
                    # 重置进度条
                    self.ui.progressBar.reset()
                    return
                sql = "insert into user(uid,username) values('%s','%s')" % (i[0], i[1])
                print(sql)
                re = db.insertDB(sql)
                print(re)
            # 获取系统当前时间
            curr_time = datetime.datetime.now()
            curTime = datetime.datetime.strftime(curr_time, '%Y-%m-%d %H:%M:%S')
            print("endTime:", curTime)

            QMessageBox.information(self.ui, "成功", "导入成功")
            sql = "select * from user left join picture on user.uid = picture.uid"
            self.data = sa.get_all_user_information(sql)
            SI.features, SI.f_uid = sa.get_all_features()
            self.present()
            self.ui.progressBar.setValue(0)
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self.ui, "错误", str(e))

    def present(self):
        # 设置表格的行数和列数
        data_len = len(self.data)
        self.ui.all_user_table.setRowCount(data_len)
        self.ui.all_user_table.setColumnCount(4)
        self.ui.all_user_table.setIconSize(QSize(100, 100))
        # 在表格中添加数据
        for i in range(data_len):
            # 设置格子高度
            self.ui.all_user_table.setRowHeight(i, 100)
            item1 = QTableWidgetItem(self.data[i][0])
            item1.setTextAlignment(Qt.AlignCenter)
            item2 = QTableWidgetItem(self.data[i][1])
            item2.setTextAlignment(Qt.AlignCenter)
            self.ui.all_user_table.setItem(i, 0, item1)
            self.ui.all_user_table.setItem(i, 1, item2)
            try:
                # 将图片加载到表格中
                item3 = QTableWidgetItem()
                item3.setFlags(Qt.ItemIsEnabled)
                item3.setIcon(QIcon(self.data[i][2]))

                item4 = QTableWidgetItem()
                item4.setFlags(Qt.ItemIsEnabled)
                item4.setIcon(QIcon(self.data[i][3]))
                self.ui.all_user_table.setItem(i, 2, item3)
                self.ui.all_user_table.setItem(i, 3, item4)
            except Exception as e:
                traceback.print_exc()
                print("record error:", e)

    def select_user_infor_from_data(self):
        username = ""
        uid = ""
        username = self.ui.user_select.text().strip()
        uid = self.ui.id_select.text().strip()
        # 获取系统当前时间
        curr_time = datetime.datetime.now()
        curTime = datetime.datetime.strftime(curr_time, '%Y-%m-%d %H:%M:%S')
        print("begin:", curTime)
        if len(username) == 0 and len(uid) == 0:
            sql = "select * from user left  join picture on user.uid = picture.uid"
        # elif len(username) != 0 and len(uid) == 0:
        #     sql = "select * from user where username = '%s' left  join picture on user.uid = picture.uid" % username
        # elif len(username) == 0 and len(uid) != 0:
        #     sql = "select * from user where uid = '%s' left  join picture on user.uid = picture.uid" % uid
        # else:
        #     sql = "select * from user where uid = '%s' and username = '%s' left  join picture on user.uid = picture.uid" % (
        #         uid, username)
        elif len(username) != 0 and len(uid) == 0:
            sql = "select * from user  left  join picture on user.username = '%s' where user.uid = picture.uid" % username
        elif len(username) == 0 and len(uid) != 0:
            sql = "select * from user  left  join picture on user.uid = '%s' where  user.uid = picture.uid" % uid
        else:
            sql = "select * from user  left  join picture on user.uid = '%s' and user.username = '%s' where user.uid = picture.uid" % (
                uid, username)

        self.data = sa.get_all_user_information(sql)
        # 获取系统当前时间
        curr_time = datetime.datetime.now()
        curTime = datetime.datetime.strftime(curr_time, '%Y-%m-%d %H:%M:%S')
        print("end:", curTime)
        self.present()

    # 将删除数据按钮绑定到槽函数
    def del_data_row(self):
        # 删除某一行的数据
        row_select = self.ui.all_user_table.selectedItems()
        print(row_select)
        if len(row_select) != 0:
            row = row_select[0].row()
            print(self.data[row])

            sql1 = "delete from features where uid = '{0}'".format(self.data[row][0])
            sql2 = "delete from user where uid = '{0}'".format(self.data[row][0])
            sql3 = "delete from picture where uid = '{0}'".format(self.data[row][0])
            sql = [sql1, sql2, sql3]
            try:
                res = db.delDB(sql)
                print(res)
                filename1 = self.data[row][2]
                filename2 = self.data[row][3]
                if os.path.exists(filename1) and len(filename1):
                    os.remove(filename1)
                    print('成功删除文件:', filename1)
                else:
                    print('未找到此文件:', filename1)
                if os.path.exists(filename2) and len(filename1):
                    os.remove(filename1)
                    print('成功删除文件:', filename2)
                else:
                    print('未找到此文件:', filename2)
            except Exception as e:
                traceback.print_exc()
                print(e)
            self.ui.all_user_table.removeRow(row)
            del self.data[row]
        SI.features, SI.f_uid = sa.get_all_features()

    # 将新增数据绑定到槽函数
    def add_btn_click(self):
        self.client = AddDialog()
        self.client.ui.show()


if __name__ == "__main__":
    app = QApplication([])
    SI.loginWin = Client3()
    SI.loginWin.ui.show()
    app.exec_()
