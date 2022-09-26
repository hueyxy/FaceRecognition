import cv2
import dlib
import numpy as np
import openpyxl
import os
import shutil
import face as fa

# from GetFeatures import *
# from lib import dataDB, share

#
# path = r"E:\PycharmProjects\面向佩戴口罩的人脸识别系统\right_excel.xlsx"
# workbook = openpyxl.load_workbook(path)
#
# # sheet1 = workbook['Sheet1']
# # cell = (sheet1['A1:B18'])
# # for i in cell:
# #     for j in i:
# #         print(j.value)
# sheet = workbook.active
# print(sheet)
# # sheet.delete_cols(idx=1, amount=2)
# img_face = r"E:\PycharmProjects\project_Qt\face_database"
# data = []
# names = []
# number = 202200000000
# i = 0
#
# for idx, a in enumerate(os.listdir(img_face)):
#     name = a.split('_')[0]
#
#     flag = a.split('_')[2].split('.')[0]
#
#     if name not in names:
#         names.append(name)
#         i += 1
#     new_num = "{:d}".format(number + i)
#
#     if flag == 'n':
#         new = new_num + "_nomask.jpg"
#     else:
#         new = new_num + "_mask.jpg"
#
#         data.append([new_num, name])
#     shutil.copy(os.path.join(img_face, a), os.path.join("temp", new))
# for row in data:
#     sheet.append(row)  # 使用append插入数据

# workbook.save("test.xlsx")
# from lib.dataDB import db
# from lib.share import SI

if __name__ == "__main__":
    # dataDB.connectDB()
    # image_paths = (r"E:\PycharmProjects\FaceRecognition2.0\temp\202200000009_mask.jpg")
    # image = cv2.imread(image_paths, cv2.IMREAD_COLOR)
    # dets = faceDetModelHandler_mask.inference_on_image(image)
    # landmarks = faceAlignModelHandler_mask.inference_on_image(image, dets[0])
    # landmarks_list = []
    # for (x, y) in landmarks.astype(np.int32):
    #     landmarks_list.extend((x, y))
    # cropped_image = face_cropper.crop_image_by_mat(image, landmarks_list)
    #
    # feature = faceRecModelHandler_mask.inference_on_image(cropped_image)
    # # np.save('temp/test1_feature.npy', feature)
    # # feature = np.load("temp/test1_feature.npy")
    # print(feature)
    # print(type(feature))
    # # fa = feature.tolist()
    # # print(fa)
    # # print(np.array(fa, dtype=np.float32))
    #
    # # sql2 = "insert into TESTBLOB  values ('%s','%s')" % (2000000, fa)
    # # result2 = dataDB.insertDB(sql2)
    # # print(result2)
    # sql = "select * from features where uid=202200000009"
    # features_all = dataDB.selectDB(sql)
    # for i in features_all:
    #     # fea = eval(i[4])
    #
    #     fea = np.array(eval(i[4]), dtype=np.float32)
    #     print(type(fea))
    #     print(fea)
    #     print("相似度", np.dot(feature, fea))
    # image_paths = "E:/PycharmProjects/project_Qt/photo/chenduling_1_y_n.jpg"
    # image = cv2.imread(image_paths)
    # fea = share.return_face_recognition_result_nonmask(image, 0)
    # image2 = cv2.imread(r"E:\PycharmProjects\FaceRecognition2.0\user_img\200013032190_mask.jpg")
    # f2 = share.return_face_recognition_result_nonmask(image2, 0)
    #
    # print(share.return_euclidean_distance(fea, fea))
    v = cv2.VideoCapture(0)
    i = 0
    while v.isOpened():
        f, img = v.read()
        cv2.imshow("st", img)
        cv2.waitKey(1)
        i += 1
        if i == 100:
            i=0
            cv2.imwrite("temp/dsh.jpg", img)
            print("OK!")
