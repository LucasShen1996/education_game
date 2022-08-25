import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

########### Cam paramiter ##################
wCam, hCam = 1920,1080
############################################
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDector(detectionCon=0.8,maxHands=1)
# initial audio
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

# volume.SetMasterVolumeLevel(-20, None)
vol = 0
vol_bar = 400
vol_per = 0
area = 0
color_volume = (0,255,0)

while True:
    success, img = cap.read()

    # Find Hand
    img = detector.findHands(img, False)
    lmList, bbox = detector.findPosition(img)
    if len(lmList) != 0:

        # Filter based on size
        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) // 100
        if 250 < area < 1000:
            # Find the distance index and Thumb
            length, img, info = detector.findDistance(4, 8, img,False)

            # Convert Volume
            vol_bar = np.interp(length, [20, 140], [400, 140])
            vol_per = np.interp(length, [20, 140], [0, 100])
            # reduce Resolution to make it smoother
            smoothness = 5
            vol_per = smoothness*round(vol_per/smoothness)
            # check finger up
            fingers = detector.fingerUp()
            print(fingers)
            # If pinky finger up
            if not fingers[4]:
                volume.SetMasterVolumeLevelScalar(vol_per/100,None)
                # cv2.circle(img, (info[4], info[5]), 10, (0, 255, 0), cv2.FILLED)
                color_volume = (0,0,255)
            else:
                color_volume = (0, 255, 0)

    # volume bar
    cv2.rectangle(img, (20, 140), (85, 400), (0, 255, 0), 3)
    cv2.rectangle(img, (20, int(vol_bar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'{int(vol_per)}%', (40, 450), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)
    cVol = int(volume.GetMasterVolumeLevelScalar()*100)
    cv2.putText(img,f'Vol set: {int(cVol)}',(400,50),cv2.FONT_HERSHEY_PLAIN,1,color_volume,3)

    # fps label
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                (0, 255, 0), 3)


    cv2.imshow("Image", img)
    cv2.waitKey(1)
