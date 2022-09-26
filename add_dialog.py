import cv2
import dlib
from PySide2 import QtGui
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QFileDialog, QMessageBox

import lib.share as sa
import lib.dataDB as db
import face as fa
from lib.share import SI
import re


class AddDialog:
    def __init__(self):
        self.ui = QUiLoader().load('ui/add_dialog.ui')
        self.ui.setWindowIcon(QIcon('img/favicon.ico'))
        self.ui.setWindowFlags(Qt.WindowCloseButtonHint)

        self.ui.input_nomask_pic.clicked.connect(self.input_nomask_pic_from_root)
        self.ui.input_mask_pic.clicked.connect(self.input_mask_pic_from_root)
        self.ui.save_btn.clicked.connect(self.save_added_data)
        self.ui.cancel_btn.clicked.connect(self.cancel_added_data)
        # 特征值
        self.nomask_features = []
        self.nomask_features_mirror = []
        self.mask_features = []
        self.mask_features_mirror = []
        # 图片
        self.nomask_pic = ""
        self.mask_pic = ""

    # 导入不戴口罩照片
    def input_nomask_pic_from_root(self):
        self.nomask_features = []
        self.nomask_features_mirror = []
        self.nomask_pic = None

        filePath, _ = QFileDialog.getOpenFileName(
            self.ui,  # 父窗口对象
            "选择你要上传的图片",  # 标题
            r"E:\\",  # 起始目录
            "图片类型 (*.png *.jpg *.bmp *jpeg)"  # 选择类型过滤项，过滤内容在括号中
        )
        print(filePath)
        img = cv2.imread(filePath)
        self.nomask_pic, self.nomask_features = sa.process_pic_from_root(img)
        # 将opencv读取的bgr格式图片转化为rgb格式
        show = cv2.cvtColor(self.nomask_pic, cv2.COLOR_BGR2RGB)
        # 转化为QLabel能放的图片格式
        showImage = QtGui.QImage(show[:], show.shape[1], show.shape[0], show.shape[1] * 3, QtGui.QImage.Format_RGB888)
        self.ui.nomask_pic.setFixedSize(150, 150)
        self.ui.nomask_pic.setPixmap(QtGui.QPixmap.fromImage(showImage))
        self.ui.nomask_pic.setScaledContents(True)

        print(">>>不戴口罩人脸特征>>>:", self.nomask_features)
        print("\n")
        print(">>>不配戴口罩镜像文件人脸特征>>>:", self.nomask_features_mirror)

    # 导入戴口罩照片
    def input_mask_pic_from_root(self):
        self.mask_features_mirror = []
        self.mask_features = []
        self.mask_pic = None
        filePath, _ = QFileDialog.getOpenFileName(
            self.ui,  # 父窗口对象
            "选择你要上传的图片",  # 标题
            r"E:\\",  # 起始目录
            "图片类型 (*.png *.jpg *.bmp *.jpeg)"  # 选择类型过滤项，过滤内容在括号中
        )
        print(filePath)
        img = cv2.imread(filePath)
        self.mask_pic, self.mask_features = sa.process_pic_from_root(img)
        show = cv2.cvtColor(self.mask_pic, cv2.COLOR_BGR2RGB)
        showImage = QtGui.QImage(show[:], show.shape[1], show.shape[0], show.shape[1] * 3, QtGui.QImage.Format_RGB888)
        self.ui.mask_pic.setFixedSize(150, 150)
        self.ui.mask_pic.setPixmap(QtGui.QPixmap.fromImage(showImage))

        print(">>>戴口罩人脸特征>>>:", self.mask_features)
        print("\n")
        print(">>>戴口罩镜像文件人脸特征>>>:", self.mask_features_mirror)

    def save_added_data(self):
        username = self.ui.input_username.text().strip()
        uid = self.ui.input_uid.text().strip()
        ret = re.match("\d{12}", uid)
        uid_len = len(uid)
        # 判断用户ID是否合法
        if ret is None or uid_len != 12:
            QMessageBox.warning(
                self.ui,
                'warning',
                '工号不合法')
            return
        try:
            sql0 = "select * from user where uid = '%s'" % uid
            results = db.selectDB(sql0)
            if len(results) != 0:
                QMessageBox.warning(
                    self.ui,
                    '错误',
                    uid + "已存在"
                )
                return
            else:
                sql1 = "insert into user(uid,username) values('{0}','{1}')".format(uid, username)
                print("sql1:", sql1)
                sql2 = "insert into features(uid,mirror,mask,featureX) values ('%s',%d,%d,'%s')," \
                       "('%s',%d,%d,'%s'),('%s',%d,%d,'%s'),('%s',%d,%d,'%s')" % (uid, 0, 0, self.nomask_features,
                                                                                  uid, 1, 0,
                                                                                  self.nomask_features_mirror,
                                                                                  uid, 0, 1, self.mask_features,
                                                                                  uid, 1, 1, self.mask_features_mirror)
                # 图片路径
                nomask_pic_path = "user_img/" + str(uid) + "_nomask.jpg"
                mask_pic_path = "user_img/" + str(uid) + "_mask.jpg"
                # 保存图片
                cv2.imencode(".jpg", self.nomask_pic)[1].tofile(nomask_pic_path)
                cv2.imencode(".jpg", self.mask_pic)[1].tofile(mask_pic_path)
                sql3 = "insert into picture(uid,mask_path,nomask_path) values ('%s','%s','%s')" % (
                    uid, mask_pic_path, nomask_pic_path)

                result1 = db.insertDB(sql1)
                result2 = db.insertDB(sql2)
                result3 = db.insertDB(sql3)
                SI.features, SI.f_uid = sa.get_all_features()
                QMessageBox.information(
                    self.ui,
                    '提示',
                    '添加成功，请继续下一步操作')
                self.ui.close()



        except Exception as e:
            db.rollback()
            QMessageBox.warning(
                self.ui,
                '错误',
                str(e)
            )

    def cancel_added_data(self):
        self.ui.close()


if __name__ == "__main__":
    app = QApplication([])
    SI.loginWin = AddDialog()
    SI.loginWin.ui.show()
    app.exec_()
