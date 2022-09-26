'''
该文件用于目标检测，返回检测结果是否佩戴口罩和人脸区域坐标（x,y,w,h)

'''
# 导入需要的库
import os
import sys
from pathlib import Path
import numpy as np
import cv2
import torch
import torch.backends.cudnn as cudnn

# 初始化目录
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # 定义YOLOv5的根目录
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # 将YOLOv5的根目录添加到环境变量中（程序结束后删除）
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from models.common import DetectMultiBackend
from utils.datasets import IMG_FORMATS, VID_FORMATS, LoadImages, LoadStreams
from utils.general import (LOGGER, check_file, check_img_size, check_imshow, check_requirements, colorstr,
                           increment_path, non_max_suppression, print_args, scale_coords, strip_optimizer, xyxy2xywh)
from utils.plots import Annotator, colors, save_one_box
from utils.torch_utils import select_device, time_sync

# 导入letterbox
from utils.augmentations import Albumentations, augment_hsv, copy_paste, letterbox, mixup, random_perspective

weights = "runs/train/exp_yolov5s/weights/best.pt"  # 权重文件地址   .pt文件
source = ROOT / 'data/images'  # 测试数据文件(图片或视频)的保存路径
data = ROOT / 'data/mask.yaml'  # 标签文件地址   .yaml文件

imgsz = (640, 640)  # 输入图片的大小 默认640(pixels)
conf_thres = 0.25  # object置信度阈值 默认0.25  用在nms中
iou_thres = 0.45  # 做nms的iou阈值 默认0.45   用在nms中
max_det = 1000  # 每张图片最多的目标数量  用在nms中
device = '0'  # 设置代码执行的设备 cuda device, i.e. 0 or 0,1,2,3 or cpu
classes = None  # 在nms中是否是只保留某些特定的类 默认是None 就是所有类只要满足条件都可以保留 --class 0, or --class 0 2 3
agnostic_nms = False  # 进行nms是否也除去不同类别之间的框 默认False
augment = False  # 预测是否也要采用数据增强 TTA 默认False
visualize = False  # 特征图可视化 默认FALSE
half = False  # 是否使用半精度 Float16 推理 可以缩短推理时间 但是默认是False
dnn = False  # 使用OpenCV DNN进行ONNX推理

# 获取设备
device = select_device(device)

# 载入模型
model = DetectMultiBackend(weights, device=device, dnn=dnn)
stride, names, pt, jit, onnx = model.stride, model.names, model.pt, model.jit, model.onnx
imgsz = check_img_size(imgsz, s=stride)  # 检查图片尺寸

# Half
# 使用半精度 Float16 推理
half &= pt and device.type != 'cpu'  # FP16 supported on limited backends with CUDA
if pt or jit:
    model.model.half() if half else model.model.float()


def detect(img):
    # 载入数据
    dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt)
    # 开始预测
    model(torch.zeros(1, 3, *imgsz).to(device).type_as(next(model.model.parameters())))
    dt, seen = [0.0, 0.0, 0.0], 0
    # 对图片进行处理
    im0 = img
    # 填充调整大小
    im = letterbox(im0, imgsz, stride, auto=pt)[0]
    # Convert HWC to CHW, BGR to RGB
    im = im.transpose((2, 0, 1))[::-1]
    im = np.ascontiguousarray(im)
    t1 = time_sync()
    im = torch.from_numpy(im).to(device)
    # uint8 to fp16/32
    im = im.half() if half else im.float()
    # 0 - 255 to 0.0 - 1.0
    im /= 255
    if len(im.shape) == 3:
        # expand for batch dim
        im = im[None]
    t2 = time_sync()
    dt[0] += t2 - t1
    # 预测
    pred = model(im, augment=augment, visualize=visualize)
    t3 = time_sync()
    dt[1] += t3 - t2
    # NMS
    pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
    dt[2] += time_sync() - t3
    # 用于存放结果
    detections = []
    max_area = 0
    # Process predictions
    for i, det in enumerate(pred):
        seen += 1
        # im0 = im0s.copy()
        if len(det):
            # Rescale boxes from img_size to im0 size
            det[:, :4] = scale_coords(im.shape[2:], det[:, :4], im0.shape).round()
            # Write results
            # 写入结果
            for *xyxy, conf, cls in reversed(det):
                xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4))).view(-1).tolist()
                xywh = [round(x) for x in xywh]
                # 检测到目标位置，格式：（left，top，w，h）
                xywh = [xywh[0] - xywh[2] // 2, xywh[1] - xywh[3] // 2, xywh[2], xywh[3]]
                area = xywh[2] * xywh[3]
                if area > max_area:
                    max_area = area
                    # 类型名
                    cls = names[int(cls)]
                    # 概率
                    conf = float(conf)
                    detections.insert(1, {'class': cls, 'conf': conf, 'position': xywh})
    # 推测的时间
    LOGGER.info(f'({t3 - t2:.3f}s)')
    return detections


if __name__ == "__main__":
    path = 'data/images/zidane.jpg'
    img = cv2.imread(path)
    # 传入一张图片
    result = detect(img)
    print(result)
