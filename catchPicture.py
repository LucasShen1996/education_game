import cv2
import time
import numpy as np
import cvzone
import HandTrackingModule as htm
import math


########### Cam paramiter ##################
wCam,hCam = 1280,720
############################################
cap = cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)
pTime = 0

detector = htm.handDector(detectionCon=0.8)
image = cv2. imread("bbb.png",cv2.IMREAD_UNCHANGED)
image = cv2.resize(image,(100,100),interpolation = cv2.INTER_AREA)
ix,iy = 300,300
cx_before,cy_before = 0,0

def overlayPNG(imgBack, imgFront, pos=[0, 0]):
    hf, wf, cf = imgFront.shape
    hb, wb, cb = imgBack.shape
    *_, mask = cv2.split(imgFront)
    maskBGRA = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGRA)
    maskBGR = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    imgRGBA = cv2.bitwise_and(imgFront, maskBGRA)
    imgRGB = cv2.cvtColor(imgRGBA, cv2.COLOR_BGRA2BGR)

    imgMaskFull = np.zeros((hb, wb, cb), np.uint8)
    imgMaskFull[pos[1]:hf + pos[1], pos[0]:wf + pos[0], :] = imgRGB
    imgMaskFull2 = np.ones((hb, wb, cb), np.uint8) * 255
    maskBGRInv = cv2.bitwise_not(maskBGR)
    imgMaskFull2[pos[1]:hf + pos[1], pos[0]:wf + pos[0], :] = maskBGRInv

    imgBack = cv2.bitwise_and(imgBack, imgMaskFull2)
    imgBack = cv2.bitwise_or(imgBack, imgMaskFull)

    return imgBack


while True:
    success , img = cap.read()
    # Find Hand
    img = cv2.flip(img,1)
    img = detector.findHands(img, False)
    lmList, bbox = detector.findPosition(img)
    if len(lmList) != 0:
        # Find the distance [4,8,12,16,20]
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        # x3, y3 = lmList[12][1], lmList[12][2]
        # x4, y4 = lmList[16][1], lmList[16][2]
        # x5, y5 = lmList[20][1], lmList[20][2]
        cx, cy = (x1 +x2 ) // 2, (y1 + y2) // 2
        # cx, cy = (x1 + x2 + x3 + x4 + x5) // 5, (y1 + y2 + y3 + y4 + y5) // 5
        length = math.hypot(x1 - x2, y1 - y2)
        # length = math.hypot(cx - x1, cy - y1) + math.hypot(cx - x2, cy - y2) + math.hypot(cx - x3, cy - y3) + math.hypot(cx - x4, cy - y4) + math.hypot(cx - x5, cy - y5)
        # area = (bbox[0]-bbox[2])*(bbox[1]-bbox[3])
        # print(area)
        if length < 20:
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
            if ix< cx < ix +100 and iy < cy < iy +100 and iy+ 50<img.shape[0] and ix + 50< img.shape[1]:
                    ix,iy = cx - 50, cy - 50
        if abs(cy - cy_before) > 50 or abs(cx - cx_before) > 50:
            cv2.putText(img, "You move to fast! ", (640, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                        (255, 0, 0), 3)
        cy_before,cx_before = cy,cx

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    if ix + 200 < img.shape[1] and iy + 200 <img.shape[0]:
        img = overlayPNG(img,image,[ix,iy])

    cv2.putText(img, "FPS: " + str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                (0, 255, 0), 3)
    cv2.imshow("Image", img)
    cv2.waitKey(1)


