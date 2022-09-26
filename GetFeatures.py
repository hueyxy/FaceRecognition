# import sys
# import cv2
# import numpy as np
# from core.model_loader.face_recognition.FaceRecModelLoader import FaceRecModelLoader
# from core.model_handler.face_recognition.FaceRecModelHandler import FaceRecModelHandler
#
# faceRecModelLoader = FaceRecModelLoader('models', 'face_recognition', "face_recognition_nonmask")
# model, cfg = faceRecModelLoader.load_model()
# # read image
# image_path = 'test_images/test1_cropped.jpg'
# image = cv2.imread(image_path)
# faceRecModelHandler = FaceRecModelHandler(model, 'cuda:0', cfg)
#
# feature = faceRecModelHandler.inference_on_image(image)
# print(feature)
# np.save('temp/test1_feature.npy', feature)


"""
@author: JiXuan Xu, Jun Wang
@date: 20201024
@contact: jun21wangustc@gmail.com
"""
import os
import sys
from tqdm import tqdm
import cv2
import numpy as np
from core.model_loader.face_detection.FaceDetModelLoader import FaceDetModelLoader
from core.model_handler.face_detection.FaceDetModelHandler import FaceDetModelHandler
from core.model_loader.face_alignment.FaceAlignModelLoader import FaceAlignModelLoader
from core.model_handler.face_alignment.FaceAlignModelHandler import FaceAlignModelHandler
from core.image_cropper.arcface_cropper.FaceRecImageCropper import FaceRecImageCropper
from core.model_loader.face_recognition.FaceRecModelLoader import FaceRecModelLoader
from core.model_handler.face_recognition.FaceRecModelHandler import FaceRecModelHandler

# 所有机型通用设置，无需修改。

# 人脸检测模型设置。

faceDetModelLoader = FaceDetModelLoader('models', 'face_detection', 'face_detection_mask')
model, cfg = faceDetModelLoader.load_model()
faceDetModelHandler_mask = FaceDetModelHandler(model, 'cuda:0', cfg)
faceDetModelLoader = FaceDetModelLoader('models', 'face_detection', 'face_detection_nonmask')
model, cfg = faceDetModelLoader.load_model()
faceDetModelHandler_nonmask = FaceDetModelHandler(model, 'cuda:0', cfg)

# face landmark model setting.

faceAlignModelLoader = FaceAlignModelLoader('models', 'face_alignment', 'face_alignment_nonmask')
model, cfg = faceAlignModelLoader.load_model()
faceAlignModelHandler_nonmask = FaceAlignModelHandler(model, 'cuda:0', cfg)

faceAlignModelLoader = FaceAlignModelLoader('models', 'face_alignment', 'face_alignment_mask')
model, cfg = faceAlignModelLoader.load_model()
faceAlignModelHandler_mask = FaceAlignModelHandler(model, 'cuda:0', cfg)

# face recognition model setting.

faceRecModelLoader = FaceRecModelLoader('models', 'face_recognition', 'face_recognition_mask')
model, cfg = faceRecModelLoader.load_model()
faceRecModelHandler_mask = FaceRecModelHandler(model, 'cuda:0', cfg)
faceRecModelLoader = FaceRecModelLoader('models', 'face_recognition', "face_recognition_nonmask")
model, cfg = faceRecModelLoader.load_model()
faceRecModelHandler_nonmask = FaceRecModelHandler(model, 'cuda:0', cfg)

# 读取图像并获取面部特征。
face_cropper = FaceRecImageCropper()
# try:
#     feature_list = []
#     list_dir = os.listdir("E:/PycharmProjects/project_Qt/photo/")
#     #for file_name in tqdm(list_dir):
#         image_paths = "E:/PycharmProjects/project_Qt/photo/chenduling_1_y_n.jpg"
#         image = cv2.imread(image_paths, cv2.IMREAD_COLOR)
#         dets = faceDetModelHandler.inference_on_image(image)
#         landmarks = faceAlignModelHandler_mask.inference_on_image(image, dets[0])
#         landmarks_list = []
#         for (x, y) in landmarks.astype(np.int32):
#             landmarks_list.extend((x, y))
#         cropped_image = face_cropper.crop_image_by_mat(image, landmarks_list)
#         cv2.imwrite("cro.jpg", cropped_image)
#         feature = faceRecModelHandler_mask.inference_on_image(cropped_image)
#         print(feature)
#         print(type(feature))
#         feature_list.append(feature)
#         for i in range(len(feature_list)):
#             score = np.dot(feature_list[0], feature_list[i])
#             logger.info('两张脸的相似度得分: %f' % score)
# except Exception as e:
#     sys.exit(-1)
