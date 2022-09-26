# 人脸录入程序界面
import sys
import time

# from PyCameraList.camera_device import list_video_devices
from PySide2 import QtGui
import cv2
from PySide2.QtGui import QIcon
from PySide2.QtUiTools import QUiLoader
from PyQt5 import QtCore, QtWidgets
import dlib
from PySide2.QtWidgets import QMessageBox
import traceback
from lib.share import SI
import lib.share as sa
import lib.dataDB as db
import face as fa
import re

# Dlib 正向人脸检测器
detector = dlib.get_frontal_face_detector()
face_cascade = cv2.CascadeClassifier("data/haarcascades/haarcascade_frontalface_default.xml")


class Client2:
    def __init__(self):
        # 从文件加载UI定义
        self.ui = QUiLoader().load("ui/information_input.ui")
        self.ui.setWindowIcon(QIcon('img/favicon.ico'))

        # 点击按钮截图
        self.ui.nomask_btn.clicked.connect(self.get_nomask_Pic)
        self.ui.nomask_btn.setEnabled(False)
        self.ui.mask_btn.clicked.connect(self.get_mask_pic)
        self.ui.mask_btn.setEnabled(False)

        self.timer_camera = QtCore.QTimer()  # 定义定时器，用于控制显示视频的帧率
        self.cap = cv2.VideoCapture()  # 视频流
        self.CAM_NUM = 0  # 为0时表示视频流来自笔记本内置摄像头

        self.timer_camera.timeout.connect(self.show_camera)  # 若定时器结束，则调用show_camera()
        self.ui.cap_btn.clicked.connect(self.button_open_camera)  # 点击按钮打开摄像头
        self.ui.cap_btn.setEnabled(False)
        self.ui.select_camera.clicked.connect(self.select_camera_num)  # 选择摄像头事件

        self.get_camera()

    def get_camera(self):
        # cameras = list_video_devices()
        # camera_dict = dict(cameras)
        camera_name = []
        # if len(camera_dict) <= 0:
        #   print("the serial port can't find！")
        #    return False
        # else:
        #   for items in range(len(camera_dict)):
        #       camera_name.append(str(items))
        # print("camera:", camera_name)
        # self.ui.cameraList.addItems(camera_name)
        camera_name.append(str(0))
        camera_name.append(str(1))
        self.ui.cameraList.addItems(camera_name)

    def select_camera_num(self):
        try:
            if not self.timer_camera.isActive():  # 若定时器未启动
                self.CAM_NUM = int(self.ui.cameraList.currentText())
                print("选择摄像头：", self.CAM_NUM)
                if self.CAM_NUM == 0:
                    self.ui.log.setText("内置摄像头准备就绪")
                else:
                    self.ui.log.setText("外置摄像头准备就绪")
                self.ui.capLabel.setPixmap(QtGui.QPixmap("img/camera_label.jpg"))
                self.ui.picLabel.setPixmap(QtGui.QPixmap("img/qql.jpg"))
                self.ui.cap_btn.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(
                self.ui,
                "选择摄像头错误",
                str(e)
            )

    def show_camera(self):
        flag, self.image = self.cap.read()  # 从视频流中读取
        self.image = cv2.flip(self.image, 1)  # 图片翻转
        show = cv2.resize(self.image, (640, 480))  # 把读到的帧的大小重新设置为 640x480
        show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)  # 视频色彩转换回RGB，这样才是现实的颜色
        self.showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], show.shape[1] * 3,
                                      QtGui.QImage.Format_RGB888)  # 把读取到的视频数据变成QImage形式
        self.ui.capLabel.setPixmap(QtGui.QPixmap.fromImage(self.showImage))  # 往显示视频的Label里 显示QImage

    def button_open_camera(self):
        try:
            if not self.timer_camera.isActive():  # 若定时器未启动
                QtWidgets.QApplication.processEvents()
                flag = self.cap.open(self.CAM_NUM)  # 参数是0，表示打开笔记本的内置摄像头，参数是视频文件路径则打开视频
                if not flag:  # flag表示open()成不成功
                    QMessageBox.warning(self.ui, 'warning', "请检查相机于电脑是否连接正确",
                                        buttons=QtWidgets.QMessageBox.Ok)
                    self.ui.log.setText("摄像头打开失败")
                else:
                    self.ui.log.setText("摄像头打开成功")
                    self.timer_camera.start(30)  # 定时器开始计时30ms，结果是每过30ms从摄像头中取一帧显示
                    self.ui.cap_btn.setText('关闭相机')
                    self.ui.cap_btn.setStyleSheet("color: rgb(255, 255, 255);\n"
                                                  "background-color: red;\n"
                                                  "border:none;\n"
                                                  "font-size:15pt;\n"
                                                  "border-radius:10px;\n"
                                                  "padding:5px;")
                self.ui.nomask_btn.setEnabled(True)
                self.ui.mask_btn.setEnabled(True)
            else:
                self.timer_camera.stop()  # 关闭定时器
                self.cap.release()  # 释放视频流
                self.ui.log.setText("摄像头关闭")

                # 设置按钮禁用
                self.ui.cap_btn.setEnabled(False)
                self.ui.nomask_btn.setEnabled(False)
                self.ui.mask_btn.setEnabled(False)

                self.ui.capLabel.clear()  # 清空视频显示区域
                self.ui.picLabel.clear()
                self.ui.capLabel.setPixmap(QtGui.QPixmap("img/camera_label.jpg"))
                self.ui.picLabel.setPixmap(QtGui.QPixmap("img/qql.jpg"))
                self.ui.cap_btn.setText('打开相机')
                self.ui.cap_btn.setStyleSheet("color: rgb(255, 255, 255);\n"
                                              "background-color: rgb(0, 255, 0);\n"
                                              "border:none;\n"
                                              "font-size:15pt;\n"
                                              "border-radius:10px;\n"
                                              "padding:5px;")
                QtWidgets.QApplication.processEvents()
                SI.features, SI.f_uid = sa.get_all_features()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(
                self.ui,
                "打开摄像头失败",
                str(e)
            )

    def get_nomask_Pic(self):
        try:
            # uid = ""
            # uname = ""
            # 获取输入用户和用户ID
            uid = self.ui.uid.text().strip()
            uname = self.ui.uname.text().strip()
            ret = re.match("\d{12}", uid)
            uid_len = len(uid)
            # 判断用户ID是否合法
            if ret is None or uid_len != 12:
                QMessageBox.warning(
                    self.ui,
                    'warning',
                    '员工号不合法')
                return

            # 如果输入用户id为空，弹窗提示
            if len(uid) == 0 or len(uname) == 0:
                QMessageBox.information(
                    self.ui,
                    '提示',
                    '请输入员工号/用户名')
                return
            else:
                # 首先判断用户基本信息是否已经导入，即user表中是否存在该uid
                sql = "select * from user where uid = '%s'" % uid
                result = db.selectDB(sql)
                # user表没有该uid 直接插入
                if len(result) == 0:
                    sql2 = "insert into user(uid,username) values('%s','%s')" % (uid, uname)
                    print("sql2:", sql2)
                    result2 = db.insertDB(sql2)
                # 已经导入到user表
                else:
                    self.ui.uname.setText(result[0][1])
                # 不管用户图片是否已经录入都可以重新插入，人脸识别要想准确就要多多益善
                img = self.image
                # img_mirror = cv2.flip(img, 1)  # 镜像文件

                # 识别人脸区域，并class,cfs,position  分类，概率，位置
                detections = fa.detect(img)
                # 将目标检测结果转化为dlib类型
                rect = sa.to_dlib_rectangle(detections[0]['position'])
                flag = detections[0]['class']
                # mirror_detections = fa.detect(img_mirror)
                # rect_mirror = sa.to_dlib_rectangle(mirror_detections[0]['position'])

                # 剪裁人脸区域
                img_blank1 = sa.cut_pic(img, rect)  # 源文件的人脸框框和截图
                # 图片颜色转化
                img_blank2 = cv2.cvtColor(img_blank1, cv2.COLOR_BGR2RGB)
                self.bk = QtGui.QImage(img_blank2.data, img_blank2.shape[1], img_blank2.shape[0],
                                       img_blank2.shape[1] * 3,
                                       QtGui.QImage.Format_RGB888)  # 把读取到的图片数据变成QImage形式
                self.ui.picLabel.setPixmap(QtGui.QPixmap.fromImage(self.bk))  # 往显示视频的Label里 显示QImage
                # 返回人脸特征点
                t1 = time.time()
                if flag == "mask":
                    fe = sa.return_face_recognition_result_mask(img, rect).tolist()  # 源文件的人脸特征点
                # fe_mirror = sa.return_face_recognition_result(img_mirror, rect_mirror).tolist()  # 镜像文件的人脸特征点
                else:
                    fe = sa.return_face_recognition_result_nonmask(img, rect).tolist()
                t2 = time.time()
                print("提取特征点时间为：", str(t2 - t1))
                # 将人脸特征点数据插入数据库
                # sql3 = "insert into features(uid,mirror,mask,featureX) values ('%s',%d,%d,'%s'),('%s',%d,%d,'%s')" % (
                #     uid, 0, 0, fe, uid, 1, 0, fe_mirror)
                sql3 = "insert into features(uid,mirror,mask,featureX) values ('%s',%d,%d,'%s')" % (uid, 0, 0, fe)
                print("插入语句：", sql3)
                db.insertDB(sql3)
                t3 = time.time()
                print("插入信息时间：", str(t3 - t2))
            # 截取人脸图片保存路径
            filePath = "user_img/" + str(uid) + "_nomask.jpg"
            '''
            如果不存在插入 存在更新
            '''
            s = "select * from picture where uid = '%s'" % uid
            results = db.selectDB(s)
            if len(results) == 0:
                s2 = "insert into picture(uid,nomask_path) values('{0}','{1}')".format(uid, filePath)
            else:
                s2 = "update picture set nomask_path = '{0}' where uid = '{1}'".format(filePath, uid)
            result5 = db.insertDB(s2)
            cv2.imencode('.jpg', img_blank1)[1].tofile(filePath)
        except Exception as e:
            traceback.print_exc()

    # 截取戴口罩照片
    def get_mask_pic(self):
        try:
            uid = ""
            uname = ""
            # 获取输入
            uid = self.ui.uid.text().strip()
            uname = self.ui.uname.text().strip()
            ret = re.match("\d{12}", uid)
            uid_len = len(uid)
            # 判断用户ID是否合法
            if ret is None or uid_len != 12:
                QMessageBox.warning(
                    self.ui,
                    'warning',
                    '员工号不合法')
                return
            # 如果输入为空 弹窗提示
            if len(uid) == 0:
                QMessageBox.information(
                    self.ui,
                    '提示',
                    '请输入用户ID')
                return
            else:
                # 首先判断用户基本信息是否已经导入
                sql = "select * from user where uid = '%s'" % uid
                result = db.selectDB(sql)
                # user表没有
                if len(result) == 0:
                    sql2 = "insert into user(uid,username) values('%s','%s')" % (uid, uname)
                    result2 = db.insertDB(sql2)

                # 已经导入到user表
                else:
                    self.ui.uname.setText(result[0][1])
                # 不管用户图片是否已经录入都可以重新插入，人脸识别要想准确就要多多益善
                img = self.image
                # img_mirror = cv2.flip(img, 1)  # 镜像文件

                # 识别人脸返回类别，概率，坐标
                detections = fa.detect(img)
                # 将目标检测结果转为dlib
                rect = sa.to_dlib_rectangle(detections[0]['position'])
                flag = detections[0]['class']
                # mirror_detections = fa.detect(img_mirror)
                # rect_mirror = sa.to_dlib_rectangle(mirror_detections[0]['position'])

                # 剪裁人脸区域
                img_blank1 = sa.cut_pic(img, rect)  # 源文件的人脸框框和截图
                # 图片颜色处理
                img_blank2 = cv2.cvtColor(img_blank1, cv2.COLOR_BGR2RGB)
                self.bk = QtGui.QImage(img_blank2.data, img_blank2.shape[1], img_blank2.shape[0],
                                       img_blank2.shape[1] * 3,
                                       QtGui.QImage.Format_RGB888)  # 把读取到的视频数据变成QImage形式
                self.ui.picLabel.setPixmap(QtGui.QPixmap.fromImage(self.bk))  # 往显示视频的Label里 显示QImage
                # 人脸特征点区域提取
                if flag == 'mask':
                    fe = sa.return_face_recognition_result_mask(img, rect).tolist()  # 源文件的人脸特征点
                else:
                    fe = sa.return_face_recognition_result_nonmask(img, rect).tolist()
                # fe_mirror = sa.return_face_recognition_result(img_mirror, rect_mirror).tolist()  # 镜像文件的人脸特征点
                # 插入
                # sql3 = "insert into features(uid,mirror,mask,featureX) values ('%s',%d,%d,'%s'),('%s',%d,%d,'%s')" % (
                #     uid, 0, 1, fe, uid, 1, 1, fe_mirror)
                sql3 = "insert into features(uid,mirror,mask,featureX) values ('%s',%d,%d,'%s')" % (uid, 0, 1, fe)
                db.insertDB(sql3)
            # 图片保存位置
            filePath = "user_img/" + str(uid) + "_mask.jpg"

            '''
            如果不存在插入 存在更新
            '''
            s = "select * from picture where uid = '%s'" % uid
            results = db.selectDB(s)
            if len(results) == 0:
                s2 = "insert into picture(uid,mask_path) values('{0}','{1}')".format(uid, filePath)
            else:
                s2 = "update picture set mask_path = '{0}' where uid = '{1}'".format(filePath, uid)
            print("采集戴口罩照片：", s2)
            result5 = db.insertDB(s2)
            cv2.imencode('.jpg', img_blank1)[1].tofile(filePath)
        except Exception as e:
            traceback.print_exc()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)  # 固定的，表示程序应用
    client = Client2()  # 实例化Ui_MainWindow
    client.ui.show()  # 调用ui的show()以显示。同样show()是源于父类QtWidgets.QWidget的
    sys.exit(app.exec_())  # 不加这句，程序界面会一闪而过
