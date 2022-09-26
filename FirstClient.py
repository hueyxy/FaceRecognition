# 人脸识别界面程序
import datetime
import time

import cv2
import dlib
from PIL import Image, ImageDraw, ImageFont
from PySide2.QtGui import Qt, QIcon
from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2 import QtWidgets
from PySide2.QtUiTools import QUiLoader
from PySide2 import QtGui, QtCore
from lib.share import SI
import lib.share as sa
import lib.dataDB as db
import traceback
# from PyCameraList.camera_device import test_list_cameras, list_video_devices, list_audio_devices
import numpy as np
import face as fa

# Dlib 正向人脸检测器
detector = dlib.get_frontal_face_detector()
# Dlib 人脸 landmark 特征点检测器
predictor = dlib.shape_predictor('data/dlib/shape_predictor_68_face_landmarks.dat')
# Dlib Resnet 人脸识别模型，提取 128D 的特征矢量
face_reco_model = dlib.face_recognition_model_v1("data/dlib/dlib_face_recognition_resnet_model_v1.dat")


class Client:
    def __init__(self):
        self.ui = QUiLoader().load('ui/face_recognition.ui')
        # self.ui.setWindowFlags(Qt.WindowCloseButtonHint)
        self.ui.setWindowIcon(QIcon('img/favicon.ico'))
        """加载人脸识别各种信息"""
        self.current_face_position = []
        self.image = cv2.imread("./img/qql.jpg")
        # 加载已录入人脸特征 和 人员姓名 下标对应
        self.features = SI.features
        self.features_names = SI.f_uid

        # 帧数
        self.frame_cnt = 0

        # 用来存储上一帧和当前帧的质心坐标
        self.last_centriod = []
        self.current_centroid = []

        # 当前帧和上一帧检测出的目标的名字
        self.current_face_name = []
        self.last_face_name = []

        # 当前帧和上一帧的人脸数
        self.current_face_cnt = 0
        self.last_face_cnt = 0

        # 存储当前摄像头中捕获到的所有人脸的坐标名称
        self.current_face_position = []
        # 存放当前帧捕获到的人脸坐标和人脸特征
        self.current_face_feature = []

        # 当前帧和上一帧的质心欧式距离
        self.last_current_distance = 0
        # 存放识别的距离
        self.current_face_distance = []

        # 控制再识别的后续帧，如果识别出未知的人脸，将reclassify_cnt计数到reclassify_interval后，对人脸进行重新识别
        self.reclassify_cnt = 0
        self.reclassify_interval = 20

        self.current_face = None

        """视频相关操作"""
        # 定义定时器，用于控制显示视频的帧率
        self.timer_camera = QtCore.QTimer()
        # 视频流
        self.cap = cv2.VideoCapture()
        # 为0时表示视频流来自笔记本内置摄像头
        self.CAM_NUM = 0

        """操作"""
        # 若定时器结束，则调用show_camera()
        self.timer_camera.timeout.connect(self.show_camera)
        # 选择打开的摄像头是内置摄像头还是外置摄像头
        self.ui.select_camera.clicked.connect(self.select_camera_num)
        # 开始识别
        self.ui.begin_btn.setEnabled(False)
        self.ui.begin_btn.clicked.connect(self.run_rec)
        # 获取可用摄像头列表
        self.get_camera()

    """获取可用摄像头列表，如果可以下载摄像头相关函数，就用注释的内容"""

    def get_camera(self):
        # cameras = list_video_devices()
        # camera_dict = dict(cameras)
        # print(camera_dict)
        camera_name = [str(0), str(1)]
        # if len(camera_dict) <= 0:
        #     print("the serial port can't find！")
        #     return False
        # else:
        #     for items in range(len(camera_dict)):
        #         camera_name.append(str(items))
        # print("camera:", camera_name)
        self.ui.cameraList.addItems(camera_name)

    """摄像头画面展示"""

    def show_camera(self):

        try:
            start_time = time.time()
            # 从视频流中读取画面
            flag, img_rd = self.cap.read()
            # 如果可以读取到画面
            if flag:
                # 将图片进行对称
                img_rd = cv2.flip(img_rd, 1)
                image = img_rd.copy()
                # 把读到的帧的大小重新设置为 640x480
                img_rd = cv2.resize(img_rd, (640, 480))
                # 检测人脸  可以检测多个人脸 返回检测结果和人脸坐标(x,y,w,h)
                detections = fa.detect(img_rd)
                ##print("人脸数：", len(detections))
                faces = []
                mask_or_not = []
                for i in detections:
                    pos = i['position']
                    # 将坐标转化为dlib类型（左上，右下）
                    face = dlib.rectangle(pos[0], pos[1], pos[0] + pos[2], pos[1] + pos[3])
                    faces.append(face)
                    mask_or_not.append(i['class'])
                ##print(">>>目标检测结果>>>:", mask_or_not)
                ##print(">>>人脸坐标>>>:", faces)

                # 展示人脸数
                self.ui.personNumber.setText(str(len(detections)))
                # 更新人脸计数器
                self.last_face_cnt = self.current_face_cnt
                self.current_face_cnt = len(detections)

                # 更新上一帧的人脸姓名列表
                self.last_face_name = self.current_face_name[:]
                # 更新上一帧和当前帧的质心列表
                self.last_centriod = self.current_centroid
                self.current_centroid = []

                # 如果当前帧和上一帧人脸数未发生变化
                if (self.current_face_cnt == self.last_face_cnt) and (self.reclassify_cnt != self.reclassify_interval):
                    # 当前人脸坐标
                    self.current_face_position = []
                    if "unknow" in self.current_face_name:
                        self.reclassify_cnt += 1
                    if self.current_face_cnt != 0:
                        # k表示第k个人脸
                        for k, d in enumerate(faces):
                            # 将每一个人脸坐标添加进当前帧人脸坐标库
                            self.current_face_position.append(tuple(
                                [faces[k].left(), int(faces[k].bottom() + (faces[k].bottom() - faces[k].top()) / 4)]))
                            # 添加当前帧质心坐标
                            self.current_centroid.append(
                                [int(faces[k].left() + faces[k].right()) / 2,
                                 int(faces[k].top() + faces[k].bottom()) / 2])
                            # 人脸矩形框
                            x1 = d.top()
                            y1 = d.left()
                            x2 = d.bottom()
                            y2 = d.right()
                            # 判断人脸区域是否超出画面范围
                            if y2 > img_rd.shape[1]:
                                y2 = img_rd.shape[1]
                            elif x2 > img_rd.shape[0]:
                                x2 = img_rd.shape[0]
                            elif y1 < 0:
                                y1 = 0
                            elif x1 < 0:
                                x1 = 0

                            # 剪裁人脸 并在右侧区域显示  此处右边人脸框在人脸数多的时候会发生变化
                            crop = img_rd[x1:x2, y1:y2]
                            self.current_face = crop
                            self.display_face(crop)

                            # 人脸框的位置
                            rect = (d.left(), d.top(), d.right(), d.bottom())
                            # 人名字标签
                            name_lab = self.current_face_name[k] if self.current_face_name != [] else ""
                            name_lab = str(name_lab) + "-" + str(mask_or_not[k])
                            # print("current_face_name:", name_lab)
                            # 画出人脸框
                            image = self.drawRectBox(image, rect, name_lab)
                            self.ui.name.setText(str(self.current_face_name[k]))
                            self.ui.maskMark.setText(str(mask_or_not[k]))

                    # 在画面中显示
                    self.display_img(image)

                    # 如果当前帧中不止一个人脸 使用质心追踪算法
                    if self.current_face_cnt != 1:
                        self.centroid_tracker()


                # 如果人脸数发生变化
                else:
                    self.current_face_position = []
                    self.current_face_distance = []
                    self.current_face_feature = []
                    self.reclassify_cnt = 0

                    # 如果人脸数为 0
                    if self.current_face_cnt == 0:
                        # 清空姓名和特征
                        self.current_face_name = []
                        self.current_face_feature = []
                        self.display_face(self.image)
                    # 人脸数增加
                    else:
                        self.current_face_name = []
                        for i in range(len(faces)):
                            if mask_or_not[i] == 'mask':
                                self.current_face_feature.append(
                                    sa.return_face_recognition_result_mask(img_rd, faces[i]))
                            else:
                                self.current_face_feature.append(
                                    sa.return_face_recognition_result_nonmask(img_rd, faces[i]))
                            self.current_face_name.append("unknow")
                        # print("self.current_face_name:", self.current_face_name)
                        for k in range(len(faces)):
                            x1 = faces[k].top()
                            x2 = faces[k].left()
                            y1 = faces[k].bottom()
                            y2 = faces[k].right()
                            self.current_face = img_rd[x1:y1, x2:y2]
                            self.current_centroid.append([int(faces[k].left() + faces[k].right()) / 2,
                                                          int(faces[k].top() + faces[k].bottom()) / 2])
                            self.current_face_distance = []
                            # 每个捕获人脸的名字坐标
                            self.current_face_position.append(tuple(
                                [faces[k].left(), int(faces[k].bottom() + (faces[k].bottom() - faces[k].top()) / 4)]))
                            # 遍历人脸库

                            for i in range(len(self.features)):
                                if self.features[i] != [] and self.current_face_feature != []:
                                    e_distance_tmp = sa.return_euclidean_distance(self.current_face_feature[k],
                                                                                  self.features[i])
                                    self.current_face_distance.append(e_distance_tmp)
                                else:
                                    self.current_face_distance.append(0.0)
                            # print("self.current_face_distance:", self.current_face_distance)
                            # 寻找出最大的欧式距离匹配
                            max_dis = max(self.current_face_distance)
                            similar_person_num = self.current_face_distance.index(max_dis)
                            if max_dis > 0.6:
                                self.current_face_name[k] = self.features_names[similar_person_num]
                                # 获取系统当前时间
                                curr_time = datetime.datetime.now()
                                curTime = datetime.datetime.strftime(curr_time, '%Y-%m-%d %H:%M:%S')
                                ##print("current_Time:", curTime)
                                # 设置图片存储路径
                                filePath = "record_img/" + str(curr_time.year) + "_" + str(curr_time.month) + "_" + str(
                                    curr_time.day) + "_" + str(curr_time.hour) + "_" + str(
                                    curr_time.minute) + "_" + str(
                                    curr_time.second) + ".jpg"
                                ##print("filePath:", filePath)
                                # 存储图片
                                cv2.imencode('.jpg', self.current_face)[1].tofile(filePath)
                                # 存储当日通行记录
                                sql = "insert into record(username,time,pic) values ('%s','%s','%s')" % (
                                    self.current_face_name[k], curTime, filePath)
                                ##print("通行记录:", sql)
                                result = db.insertDB(sql)
                end_time = time.time()
                if end_time == start_time:
                    use_time = 1
                else:
                    use_time = end_time - start_time
                fps = int(1.0 / round(use_time, 3))
                self.ui.fps.setText(str(fps) + " 37.0")
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(
                self.ui,
                "人脸识别错误",
                str(e)
            )

    """摄像头选择事件"""

    def select_camera_num(self):
        try:
            if not self.timer_camera.isActive():  # 若定时器未启动
                self.CAM_NUM = int(self.ui.cameraList.currentText())
                print("self.CAM_NUM:", self.CAM_NUM)
                if self.CAM_NUM == 0:
                    self.ui.log.setText("内置摄像头准备就绪")
                else:
                    self.ui.log.setText("外置摄像头准备就绪")
                # 初始化数据
                self.ui.name.setText("unknow")
                self.ui.maskMark.setText("nomask")
                self.ui.personNumber.setText("0")
                self.ui.fps.setText("0")
                self.ui.cameraLabel.setPixmap(QtGui.QPixmap("img/camera_label.jpg"))
                self.ui.personX.setPixmap(QtGui.QPixmap("img/qql.jpg"))
            self.ui.begin_btn.setEnabled(True)

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(
                self.ui,
                "摄像头选择函数出错了",
                str(e)
            )

    """画人脸框"""

    def drawRectBox(self, image, rect, addText):
        try:
            cv2.rectangle(image, (int(round(rect[0])), int(round(rect[1]))),
                          (int(round(rect[2])), int(round(rect[3]))),
                          (0, 0, 255), 2)
            cv2.rectangle(image, (int(rect[0] - 1), int(rect[1]) - 16), (int(rect[0] + 75), int(rect[1])), (0, 0, 255),
                          -1, cv2.LINE_AA)
            img = Image.fromarray(image)
            draw = ImageDraw.Draw(img)
            font_path = "Font/platech.ttf"
            font = ImageFont.truetype(font_path, 14, 0)
            draw.text((int(rect[0] + 1), int(rect[1] - 16)), addText, (255, 255, 255), font=font)
            imagex = np.array(img)
            return imagex
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(
                self.ui,
                "画人脸框错误",
                str(e)
            )

    """加载视频区域"""

    def display_img(self, image):
        try:
            # self.label_display.clear()
            image = cv2.resize(image, (640, 480))  # 设定图像尺寸为显示界面大小
            show = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], show.shape[1] * 3,
                                     QtGui.QImage.Format_RGB888)
            self.ui.cameraLabel.setPixmap(QtGui.QPixmap.fromImage(showImage))
            self.ui.cameraLabel.setScaledContents(True)
            QtWidgets.QApplication.processEvents()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(
                self.ui,
                "加载视频区域错误",
                str(e)
            )

    """在右边小框显示人脸"""

    def display_face(self, image):
        try:
            # 清空右侧显示区域
            self.ui.personX.clear()
            if image.any():
                # 图片颜色转化
                show = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], show.shape[1] * 3,
                                         QtGui.QImage.Format_RGB888)
                self.ui.personX.setFixedSize(200, 200)
                self.ui.personX.setPixmap(QtGui.QPixmap.fromImage(showImage))
                self.ui.personX.setScaledContents(True)
                QtWidgets.QApplication.processEvents()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(
                self.ui,
                "显示人脸框错误",
                str(e)
            )

    """ 使用质心追踪来识别人脸"""

    def centroid_tracker(self):
        for i in range(len(self.current_centroid)):
            distance_current_person = []
            # 计算不同对象间的距离
            for j in range(len(self.last_centriod)):
                self.last_current_distance = sa.return_euclidean_distance(
                    self.current_centroid[i], self.last_centriod[j])

                distance_current_person.append(self.last_current_distance)

            last_frame_num = distance_current_person.index(max(distance_current_person))
            self.current_face_name[i] = self.last_face_name[last_frame_num]

    """点击开始运行按钮执行函数"""

    def run_rec(self):
        self.features, self.features_names = sa.get_all_features()
        try:
            # 如果定时器未启动
            if not self.timer_camera.isActive():
                QtWidgets.QApplication.processEvents()
                flag = self.cap.open(self.CAM_NUM)
                # flag = self.cap.open(r"./12.mp4")
                if not flag:
                    QMessageBox.critical(
                        self.ui,
                        "错误",
                        "摄像头打开失败，请检查连接后重新打开"
                    )
                else:
                    self.ui.log.setText("正在打开摄像头，请稍等")
                    # 打开定时器
                    self.timer_camera.start(30)
                    # 将摄像头按钮的文字置为结束识别
                    self.ui.begin_btn.setText("结束识别")
                    self.ui.log.setText("摄像头打开成功")
                    self.ui.begin_btn.setStyleSheet("background-color: red;\n"
                                                    "color: rgb(255, 255, 255);\n"
                                                    "font: 87 14pt \"Arial Black\";\n"
                                                    "border-radius:10px;")
                    self.features = SI.features
                    self.features_names = SI.f_uid
            else:
                # 关闭定时器
                self.timer_camera.stop()
                # 释放视频流
                self.cap.release()
                self.ui.log.setText("摄像头已关闭")
                # 清空视频显示区域
                self.ui.cameraLabel.clear()
                self.ui.personX.clear()
                self.ui.cameraLabel.setPixmap(QtGui.QPixmap("img/camera_label.jpg"))
                self.ui.personX.setPixmap(QtGui.QPixmap("img/qql.jpg"))
                # 重置识别按钮
                self.ui.begin_btn.setText("开始识别")
                self.ui.begin_btn.setStyleSheet("background-color: rgb(104, 164, 253);\n"
                                                "color: rgb(255, 255, 255);\n"
                                                "font: 87 14pt \"Arial Black\";\n"
                                                "border-radius:10px;")
                # 重置区域文字
                self.ui.name.setText("unknow")
                self.ui.maskMark.setText("nomask")
                self.ui.personNumber.setText("0")
                self.ui.fps.setText("0")
                QtWidgets.QApplication.processEvents()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(
                self.ui,
                "打开摄像头错误",
                str(e)
            )


if __name__ == "__main__":
    app = QApplication([])
    SI.loginWin = Client()
    SI.loginWin.ui.show()
    app.exec_()
