from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton, QProgressBar, QMessageBox
from time import sleep
from threading import Thread
from PySide2.QtCore import Signal, QObject


# 信号库
class SignalStore(QObject):
    # 定义一种信号
    progress_update = Signal(int)
    # 还可以定义其他作用的信号


# 实例化
so = SignalStore()


class Stats():
    def __init__(self):
        # 连接信号到处理的slot函数
        so.progress_update.connect(self.setProgress)

        self.window = QMainWindow()
        self.window.resize(500, 400)
        self.window.move(300, 300)

        self.progressBar = QProgressBar(self.window)
        self.progressBar.resize(300, 20)
        self.progressBar.move(80, 30)
        # 进度是 0 - 5，
        self.progressBar.setRange(0, 5)

        self.button = QPushButton('统计', self.window)
        self.button.move(80, 80)

        self.button.clicked.connect(self.handleCalc)

        # 统计进行中标记，不能同时做两个统计
        self.ongoing = False

    def handleCalc(self):
        def workerThreadFunc():
            self.ongoing = True
            for i in range(1, 6):
                sleep(1)
                # 发出信息，通知主线程进行进度处理
                so.progress_update.emit(i)
            self.ongoing = False

        if self.ongoing:
            QMessageBox.warning(
                self.window,
                '警告', '任务进行中，请等待完成')
            return

        worker = Thread(target=workerThreadFunc)
        worker.start()

    # 处理进度的slot函数
    def setProgress(self, value):
        self.progressBar.setValue(value)


app = QApplication([])
stats = Stats()
stats.window.show()
app.exec_()