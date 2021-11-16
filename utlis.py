from djitellopy import Tello
import cv2
import numpy as np
from matplotlib import pyplot as plt
import time
import sys



def initializeTello():
    myDrone = Tello()
    myDrone.connect()
    myDrone.for_back_velocity = 0
    myDrone.left_right_velocity = 0
    myDrone.up_down_velocity = 0
    myDrone.yaw_velocity = 0
    myDrone.speed = 0
    print("battery: " + myDrone.get_battery() + "%")
    myDrone.streamoff()
    myDrone.streamon()
    return myDrone


def telloGetFrame(myDrone, w=360, h=240):
    myFrame = myDrone.get_frame_read()
    myFrame = myFrame.frame
    img = cv2.resize(myFrame,(w,h))
    return img

def findFace(img):
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(imgGray,1.1,6)

    myFaceListC = []
    myFaceListArea = []

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cx = x + w // 2
        cy = y + h // 2
        area = w * h
        myFaceListArea.append(area)
        myFaceListC.append([cx, cy])

    if len(myFaceListArea) != 0:
        i = myFaceListArea.index(max(myFaceListArea))
        return img, [myFaceListC[i],myFaceListArea[i]]
    else:
        return img, [[0,0],0]


def trackFace(myDrone, info, w, h, pid, pError, fbRange):
    area = info[1]
    x, y = info[0]

    error = x-w // 2
    speed = pid[0] * error + pid[1] * (error - pError)
    speed = int(np.clip(speed, -100, 100))

    #forward and backward
    if area > fbRange[0] and area < fbRange[1]:
        myDrone.for_back_velocity = 0
    elif area > fbRange[1]:
        myDrone.for_back_velocity = -20
    elif area < fbRange[0] and area != 0:
        myDrone.for_back_velocity = 20
    else:
        myDrone.for_back_velocity = 0

    #up and down
    if(y != 0):
        print(y)
    if y > h-10 and y < h+10:
        myDrone.up_down_velocity = 0
    elif y > h+10:
        myDrone.up_down_velocity = -20
    elif y < h-10 and y != 0:
        myDrone.up_down_velocity = 20
    else:
        myDrone.up_down_velocity=0

    if x != 0:
        myDrone.yaw_velocity = speed
    else:
        myDrone.yaw_velocity = 0

    if myDrone.send_rc_control:
         myDrone.send_rc_control(myDrone.left_right_velocity,
                                 myDrone.for_back_velocity,
                                 myDrone.up_down_velocity,
                                 myDrone.yaw_velocity)
    return error




# def findQR(img):
#     faceCascade = cv2.CascadeClassifier('final_project_QRcode.jpg')
#     imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     faces = faceCascade.detectMultiScale(imgGray,1.1,6)
#     inputImage = cv2.imread("final_project_QRcode.jpg")
#
#     # Display barcode and QR code location
#     def display(im, bbox):
#         n = len(bbox)
#         for j in range(n):
#             cv2.line(im, tuple(bbox[j][0]), tuple(bbox[(j + 1) % n][0]), (255, 0, 0), 3)
#
#         # Display results
#         cv2.imshow("Results", im)
#
#     qrDecoder = cv2.QRCodeDetector()
#
#     # Detect the qrcode
#     data, bbox, rectifiedImage = qrDecoder.detect(inputImage)
#     if len(data) > 0:
#         print("Decoded Data : {}".format(data))
#         display(inputImage, bbox)
#         rectifiedImage = np.uint8(rectifiedImage);
#         cv2.imshow("Rectified QRCode", rectifiedImage);
#     else:
#         print("QR Code not detected")
#         cv2.imshow("Results", inputImage)
#
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
#
#     myFaceListC = []
#     myFaceListArea = []
#
#     for (x, y, w, h) in faces:
#         cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
#         cx = x + w // 2
#         cy = y + h // 2
#         area = w * h
#         myFaceListArea.append(area)
#         myFaceListC.append([cx,cy])
#
#     if len(myFaceListArea) != 0:
#         i = myFaceListArea.index(max(myFaceListArea))
#         return img, [myFaceListC[i],myFaceListArea[i]]
#     else:
#         return img, [[0,0],0]