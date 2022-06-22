
# importing required libraries
#
# from tarfile import TarFile
import torch
import cv2
import time
import numpy as np
import os
import sys
# import argparse

# trackers
from mylib.centroidtracker_move import CentroidTracker
from mylib.trackableobject_delaysolved import TrackableObject
from collections import OrderedDict

import json
from PIL import Image


# AK code
import socketio
import paramiko

BASE_URL = "http://192.168.1.150:9000"
MISSED_TAG_PATH_BASE_URL = "/home/frinksacckymore002/acc-backend"
SCP_PATH_BASE_URL = "/home/frinksacckymore001/acc-backend"

sio = socketio.Client()
sio.connect(BASE_URL)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.150', username='frinksacckymore001',
            password='Frinks@2020')
sftp = ssh.open_sftp()

# --------------   GLOBAL VARIABLES   ---------------------

print("[INFO] Reading json file and loading model parameters")

# reading parameter json file
data_jsonx = json.load(open(
    "/home/frinksacckymore002/acc-backend/scripts/label_bag_tag/model_files/model_parameters_slave.json",))
data_jsonx = data_jsonx[0]


VID_OUT = data_jsonx['VID_OUT']  # "./detections"
SAVE_FRAME = data_jsonx['SAVE_FRAME']
IM_SHOW = data_jsonx['IM_SHOW']

FRAME_SKIP = data_jsonx['FRAME_SKIP']
AFTER_FRAME = 1  # 1350 ## 3500
# ROIX_DISTANCE = data_jsonx['ROIX_DISTANCE'] ### a ROI is created at a distance of 500 pxl away from centroid. Count information will be updated when a bag crosses this ROI

DETECT_ONLY_AFTER_CX = data_jsonx['DETECT_ONLY_AFTER_CX']  # 245
DETECT_ONLY_AFTER_CY = data_jsonx['DETECT_ONLY_AFTER_CY']

DIRECTION_DICT = {0: "left2right", 1: "right2left"}

SCORE_THRESHOLD_BAG = data_jsonx['SCORE_THRESHOLD_BAG']
SCORE_THRESHOLD_TAG = data_jsonx['SCORE_THRESHOLD_TAG']
IOU_THRESHOLD_BAG = data_jsonx['IOU_THRESHOLD_BAG']
IOU_THRESHOLD_TAG = data_jsonx['IOU_THRESHOLD_TAG']


# BAG_MODEL_WEIGHT = '/home/frinks1/Downloads/DP/Heidelberg/label_bag/yolov5l_training_results/training_backup_800_data_640ims_COCO_ADAM_cstmHyp_hJsw/weights/epoch130.pt'
#BAG_MODEL_WEIGHT = f"./model_files/{data_jsonx['BAG_MODEL_WEIGHT']}"
# TAG_MODEL_WEIGHT = '/home/frinks1/Downloads/DP/Heidelberg/label_tag/yolov5l_training_results_data/training_backup_1135dt_coco_hype_adam_hJsw/weights/best.pt'
# TAG_MODEL_WEIGHT = f"./model_files/{data_jsonx['TAG_MODEL_WEIGHT']}"
BAG_MODEL_WEIGHT = f"{data_jsonx['BAG_MODEL_WEIGHT']}"
# TAG_MODEL_WEIGHT = '/home/frinks1/Downloads/DP/Heidelberg/label_tag/yolov5l_training_results_data/training_backup_1135dt_coco_hype_adam_hJsw/weights/best.pt'
TAG_MODEL_WEIGHT = f"{data_jsonx['TAG_MODEL_WEIGHT']}"

# reading information about the belt
BELT_MASTER = ['1', '2', '3', '4', '5']
B1_LINK, B1_DIR, B1_ROIX, B1_ROICOUNT = data_jsonx["1"]
B2_LINK, B2_DIR, B2_ROIX, B2_ROICOUNT = data_jsonx["2"]
B3_LINK, B3_DIR, B3_ROIX, B3_ROICOUNT = data_jsonx["3"]
B4_LINK, B4_DIR, B4_ROIX, B4_ROICOUNT = data_jsonx["4"]
B5_LINK, B5_DIR, B5_ROIX, B5_ROICOUNT = data_jsonx["5"]

################

# BASE PARAMETERS
RTSP_LINKS = [B1_LINK, B2_LINK, B3_LINK, B4_LINK, B5_LINK]
vid_directions = [B1_DIR, B2_DIR, B3_DIR, B4_DIR, B5_DIR]
roix_master = [B1_ROIX, B2_ROIX, B3_ROIX, B4_ROIX, B5_ROIX]
roi_count = [B1_ROICOUNT, B2_ROICOUNT, B3_ROICOUNT, B4_ROICOUNT, B5_ROICOUNT]
transaction_id_master = ["", "", "", "", ""]
beltid_master = BELT_MASTER
belt_activated = [False, False, False, False, False]
belt_limit = [0, 0, 0, 0, 0]


def socket_function(bbelt_id, tra_id, limit):
    if str(bbelt_id) in BELT_MASTER:
        index_value = BELT_MASTER.index(str(bbelt_id))
        transaction_id_master[index_value] = str(tra_id)
        belt_limit[index_value] = int(limit)
        belt_activated[index_value] = True


def stopping_belt_function(belt_id):
    print(f"stopping belt id:{belt_id}")
    if str(belt_id) in BELT_MASTER:
        index_value = BELT_MASTER.index(str(belt_id))
        transaction_id_master[index_value] = ""
        belt_limit[index_value] = 0
        belt_activated[index_value] = False

# AK code


@sio.on('service')
def on_message(data):
    socket_function(data["printing_belt_id"],
                    data["transaction_id"], data["bag_count_limit"])


@sio.on('stop')
def on_message(data):
    stopping_belt_function(data["printing_belt_id"])

# print(f"[INFO] ---------------- MODEL PARAMETERS ARE: ----------------------\n")
# print(f"VID_OUT = {VID_OUT}, \nSAVE_FRAME = {SAVE_FRAME}, \nIM_SHOW = {IM_SHOW}, \nFRAME_SKIP = {FRAME_SKIP}, \nROIX_DISTANCE = {ROIX_DISTANCE}, \nDETECT_ONLY_AFTER_CX = {DETECT_ONLY_AFTER_CX}, \nDETECT_ONLY_AFTER_CY = {DETECT_ONLY_AFTER_CY}, \nSCORE_THRESHOLD_BAG = {SCORE_THRESHOLD_BAG}, \nIOU_THRESHOLD_BAG = {IOU_THRESHOLD_BAG}, \nSCORE_THRESHOLD_TAG = {SCORE_THRESHOLD_TAG},\nIOU_THRESHOLD_TAG = {IOU_THRESHOLD_TAG}, \nBAG_MODEL_WEIGHT = {BAG_MODEL_WEIGHT} ,\nTAG_MODEL_WEIGHT{TAG_MODEL_WEIGHT}")


# -------------------------------------- function to run detection ---------------------------------------------------------
def detectx(frame_batch, model):

    # results = model(frame_batch, augment=True) ### with TTA
    results = model(frame_batch)

    # loopting through detections w.r.t image in order to create the final result_file

    batch_results = []

    for ir in range(len(results)):

        labels, cordinates = results.xyxyn[ir][:, -
                                               1], results.xyxyn[ir][:, :-1]

        batch_results.append((labels, cordinates))

    return batch_results


def detectx_tag(frame_batch, model):

    results = model(frame_batch, augment=True)  # with TTA
    # results = model(frame_batch)

    # loopting through detections w.r.t image in order to create the final result_file

    batch_results = []

    for ir in range(len(results)):

        labels, cordinates = results.xyxyn[ir][:, -
                                               1], results.xyxyn[ir][:, :-1]

        batch_results.append((labels, cordinates))

    return batch_results

# ------------------------------------ to plot the BBox and results --------------------------------------------------------


def update_rects_plot_bbox(batch_results, imgs_rgb, classes, frame_no, transactionid_master, beltid_master):
    """
    --> This function takes results, frame and classes
    --> results: contains labels and coordinates predicted by model on the given frame
    --> classes: contains the strting labels

    """

    imgs_results = []
    rects_master = []
    x_mid = []

    for im in range(len(imgs_rgb)):

        frame = imgs_rgb[im]
        labels, cord = batch_results[im]
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        x_mid.append(x_shape//2)

        rects = []  # rects per image

        # to save the raw frame without any annotation on it if the threshold of any detected obect is < threshold value
        frame_forsave = frame.copy()

        # looping through the detections per image
        for i in range(n):
            row = cord[i]
            # threshold value for detection. We are discarding everything below this value
            if row[4] >= SCORE_THRESHOLD_BAG:
                # print(f"[INFO] Extracting BBox coordinates. . . ")
                x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(
                    row[2]*x_shape), int(row[3]*y_shape)  # BBOx coordniates
                # startX, startY, endX, endY = x1,y1,x2,y2
                text_d = classes[int(labels[i])]

                cx = int((x1+x2)/2.0)
                cy = int((y1+y2)/2.0)

                if text_d == 'cement_bag':

                    # print(f"----------- centroid before passing value for tracking: (cx,cy) ---> {(cx,cy)}")
                    # and (cy>DETECT_ONLY_AFTER_CY): #### to filter out wrong detection on person moving in the background
                    if (cx > DETECT_ONLY_AFTER_CX):

                        cv2.rectangle(frame, (x1, y1), (x2, y2),
                                      (0, 0, 255), 2)  # BBox

                        # cv2.putText(frame, text_d + f" {round(float(row[4]),2)}", (x1, y1-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(255,255,255), 2)

                        # without probability
                        cv2.putText(
                            frame, text_d, (x1, y1-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                        rects.append((x1, y1, x2, y2))

            # code to save frames less than threshold

            elif (row[4] < SCORE_THRESHOLD_BAG) and (0.4 < row[4]):

                x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(
                    row[2]*x_shape), int(row[3]*y_shape)  # BBOx coordniates
                width = x2 - x1
                height = y2 - y1

                area = width * height

                # # this is to filter out detections with very small area (like small portion of the bag is visible at corner of the screen)
                # if area > 50000:
                #     # print(f"row[4]: {row[4]}")
                #     # saving frames with detection below threshold values
                #     # os.makedirs(f"./detections/less_th_bag/", exist_ok=True)
                #     cv2.imwrite(
                #         f"./detections/less_th_bag/{transactionid_master[im]}_{beltid_master[im]}_f{frame_no}_dn{n}_th{round(float(row[4]),5)}.jpg", frame_forsave)

        imgs_results.append(frame)
        rects_master.append(rects)

    return imgs_results, rects_master, x_mid

# --------------------------------------------------------- tracker function -------------------------------------------------------


def tracker_im(frame, objects, trackableObject, movement_direction, ROIX_DISTANCE):
    # print(f"[INFO] Tracking and counting. . . ")

    image_h, image_w, _ = frame.shape
    # print(f"--------------------------------- vid direction inside tracker_im: {movement_direction}")

    # loop through the tracked objects
    for (objectID, centroid) in objects.items():

        # print(f"inside tracked object loop")
        # check to see if a trackable object exists for the current object ID
        to = trackableObject.get(objectID, None)

        # if there is no existing trackable object,create one
        if to is None:
            to = TrackableObject(objectID, centroid)

        # if there is a trackable object, it can be used
        else:

            # the difference between the y-coordinate of the *current* centroid and the mean of *previous* centroids will tell us in which direction the object is moving (negative for
            # 'up' and positive for 'down')
            # x = [c[0] for c in to.centroids]

            # direction = centroid[0] - np.mean(x)
            to.centroids.append(centroid)

            # print(f"----->>> direction : {direction} ------------------")

            # check to see if the object has been counted or not

            if not to.counted:

                # if the direction is negative and the centroid is above the threshold line,
                #  then the object is moving from right to left

                if movement_direction == 'left2right':
                    # custom ROI to do counting, image_w//2: is ideal condition
                    if centroid[0] > ROIX_DISTANCE:

                        to.counted = True

                else:  # moving right2left
                    if centroid[0] < ROIX_DISTANCE:  # image_w//2:

                        to.counted = True

        # store the trackable object inside the dictionary
        trackableObject[objectID] = to

        # draw the ID of the object and centroid of the object on the output frame
        ob_id = "ID {}".format(objectID)
        # cv2.putText(frame, ob_id,(centroid[0] - 10, centroid[1] - 10),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0, 255), 2)
        # cv2.putText(frame, f"{(centroid[0], centroid[1])}",(centroid[0] - 50, centroid[1] - 50),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0, 255), 2)
        cv2.circle(frame, (centroid[0], centroid[1]), 5, (255, 0, 0), -1)

    return frame, trackableObject


# ------------------------------------ to plot the BBox and result of LABEL TAG--------------------------------------------------------
def label_tag_plot_bbox(batch_results, imgs_rgb, classes, frame_no):
    """
    --> This function takes results, frame and classes
    --> results: contains labels and coordinates predicted by model on the given frame
    --> classes: contains the strting labels

    """
    # print(imgs_rgb)
    imgs_results = []
    result_tag_master = []

    for im in range(len(imgs_rgb)):
        # image_h, image_w, _ = frame.shape

        frame = imgs_rgb[im]
        labels, cord = batch_results[im]
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]

        # to save the raw frame without any annotation on it if the threshold of any detected obect is < threshold value
        frame_forsave = frame.copy()

        # print(f"[INFO] Total {n} tag detections. . . ")
        # print(f"[INFO] Looping through all detections. . . ")

        if n != 0:
            # looping through the detections per image
            for i in range(n):
                row = cord[i]
                # threshold value for detection. We are discarding everything below this value
                if row[4] >= SCORE_THRESHOLD_TAG:
                    # print(f"[INFO] Extracting BBox coordinates. . . ")
                    x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(
                        row[2]*x_shape), int(row[3]*y_shape)  # BBOx coordniates
                    # startX, startY, endX, endY = x1,y1,x2,y2
                    text_d = classes[int(labels[i])]

                    cv2.rectangle(frame, (x1, y1), (x2, y2),
                                  (0, 255, 0), 2)  # BBox
                    # cv2.putText(frame, text_d + f" {round(float(row[4]),2)}", (x1, y1-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,0,0), 2)
                    # cv2.putText(frame, text_d + f" {round(float(row[4]),2)}", (x1-80, y1-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,0,0), 2)

                    # without probability
                    cv2.putText(frame, text_d, (x1-80, y1-20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

                # code to save frames less than threshold

                elif (row[4] < SCORE_THRESHOLD_TAG) and (0.2 < row[4]):

                    x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(
                        row[2]*x_shape), int(row[3]*y_shape)  # BBOx coordniates
                    width = x2 - x1
                    height = y2 - y1

                    # area = width * height

                    # if area > 300000:  #### this is to filter out detections with very small area (like small portion of the bag is visible at corner of the screen)
                    #     print(f"row[4]: {row[4]}")
                    # saving frames with detection below threshold values
                    # os.makedirs(f"./detections/less_th_tag/", exist_ok=True)
                    # cv2.imwrite(
                    #     f"./detections/less_th_tag/f{frame_no}_dn{n}_th{round(float(row[4]),5)}.jpg", frame_forsave)

            imgs_results.append(frame)
            result_tag_master.append(True)
        else:
            imgs_results.append(frame)
            result_tag_master.append(False)

    return imgs_results, result_tag_master


# ------------------------------------------------------------------ Main function ---------------------------------------------------------------------------------------------------

def main():  # img_path = Full path to image

    # checking that len of all input arrays should be same
    len_check = True

    try:
        assert len(RTSP_LINKS) == len(vid_directions) == len(roix_master) == len(
            roi_count) == len(transaction_id_master) == len(beltid_master)
    except:
        len_check = False

    # roi sanity check
    '''
    - for direction left2right: roix value < roi count
    - for direction right2left: roix value > roi count
    - As the bags are getting counted and checked for tag after roix value and all the count values (bag and tag) are being updated after roi count value 
    
    '''
    roi_sanity = True
    for i in range(len(vid_directions)):
        if vid_directions[i] == 0:  # left2right
            if roix_master[i] < roi_count[i]:
                roi_sanity = True
            else:
                roi_sanity = False
                break

        if vid_directions[i] == 1:  # right2lft
            if roix_master[i] > roi_count[i]:
                roi_sanity = True
            else:
                roi_sanity = False
                break

    if roi_sanity == False:
        print(f"[ERROR] Please check the roi values according to directions.")
        sys.exit(1)  # exiting

    # entering into main area

    if len_check:  # len(RTSP_LINKS) == len(vid_directions): ## len of all input arrays should be same

        VID_DIRECTION = [DIRECTION_DICT[i] for i in vid_directions]

        try:
            print(f"[INFO] Loading model... ")
            # loading the custom trained model
            # model =  torch.hub.load('ultralytics/yolov5', 'custom', path='bestm_label_bag.pt',force_reload=True) ## if you want to download the git repo and then run the detection
            # lastm_label_bag.pt--good result,  The repo is stored locally
            model = torch.hub.load(f'./yolov5-master',
                                   'custom', source='local', path=BAG_MODEL_WEIGHT, force_reload=True)
            # model.conf = SCORE_THRESHOLD_BAG ### setting up confidence threshold
            model.iou = IOU_THRESHOLD_BAG  # setting up iou threshold

            classes = model.names  # class names in string format

            # tag detection model
            model_tag = torch.hub.load(f'./yolov5-master', 'custom', source='local',
                                       path=TAG_MODEL_WEIGHT, force_reload=True)  # The repo is stored locally
            # model_tag =  torch.hub.load('./yolov5-master', 'custom', source ='local', path=TAG_MODEL_WEIGHT,force_reload=True,device='cpu') ### The repo is stored locally
            # model_tag.conf = SCORE_THRESHOLD_TAG ### setting up confidence threshold
            model_tag.iou = IOU_THRESHOLD_TAG  # setting up iou threshold

        except Exception as e:

            # print(f"\n\n ----------------------------------------------------------------------------ERROR!!!!!! :\n {e}\n\n")
            print(
                f"\n[ERROR] Failed to load model!!! Please check the model path. Exiting... \n ")

            sys.exit(1)  # exiting

        # to create windows according to the no. of videos in RTSP links
        # if IM_SHOW:
        #     for i in range(len(RTSP_LINKS)):
        #         cv2.namedWindow(f'{i}', cv2.WINDOW_NORMAL)

        # ------------------------------------------------------ TRACKERS --------------------------------------------------------------------

        master_ct = []  # [ct_label_1,ct_label_2,ct_label_3,ct_label_4,ct_label_5]
        # [trackableObject_label_1, trackableObject_label_2 ,trackableObject_label_3, trackableObject_label_4, trackableObject_label_5]
        master_trackableObject = []
        label_tag_count_master = []  # [0,0,0,0,0]
        total_bag_master = []  # [0,0,0,0,0]

        # creating different objects for each and every videos in the RTSP link
        for i in range(len(RTSP_LINKS)):
            master_ct.append(CentroidTracker())
            master_trackableObject.append({})
            label_tag_count_master.append(0)
            total_bag_master.append(0)

        # -------------------------------------------------- readnig frames directly from videos --------------------------------------------------------------
        master_video = []  # [video1 ,video2,video3,video4,video5]

        for i in range(len(RTSP_LINKS)):

            master_video.append(cv2.VideoCapture(RTSP_LINKS[i]))

        # CREATING VIDEO WRITERS TO SAVE VIDEO
        # if VID_OUT:

        #     video_writer_master = [] ### [out1, out2, out3, out4, out5]

        #     for vw in range(len(master_video)):

        #         vc = master_video[vw]

        #         # by default VideoCapture returns float instead of int
        #         width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
        #         height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))
        #         fps = 8  # int(vid.get(cv2.CAP_PROP_FPS))
        #         codec = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        #         out1 = cv2.VideoWriter(f"{VID_OUT}/{vw}_tag.mp4", codec, fps, (width, height))

        #         video_writer_master.append(out1)

        # --------------------------------------- fps parameters ----------------------------------------------------

        LOOP_NO = 1
        fps_lookup = 1
        fps_99 = []

        detection_time = []
        detection_tracker_time = []

        FRAME_COUNTER = 1

        # -------------------------------- main while loop for looping through the videos ------------------------------

        print(f"[INFO] Working with video link ... ")

        while True:

            try:
                # print(f"--------------------------------------------------------------- WORKING WITH FRAME: {FRAME_COUNTER} --------------------------------------------- ")
                st = time.time()
                '''
                IDEAS:
                - to activate and deactivate cameras. i.e. the whole process will be started with black images and then when a camera gets activated, its images will replace the black image at the corresponding index of img_master
                - to deactivate the camera after the count reached the user defined limit
                - to activate cameras in the middle of already running detections, i.e. let's say already there are 2 cameras running and you want to activate a 3rd camera 

                '''

                # this list contains frames from all the videos i.e. image batch creaded by combining the frames from all the videos
                img_master = [np.zeros((750, 1000, 3), dtype=np.float32), np.zeros((750, 1000, 3), dtype=np.float32), np.zeros((750, 1000, 3), dtype=np.float32), np.zeros(
                    (750, 1000, 3), dtype=np.float32), np.zeros((750, 1000, 3), dtype=np.float32)]  # [img1,img1,img1,img1,img1] ----> frame 1 from all videos

                # img_master=[]   ### [img1,img1,img1,img1,img1] ----> frame 1 from all videos

                # checking if the bag count crossed the counting limit for the particular bag
                for i in range(len(RTSP_LINKS)):

                    # first we area checking.. wheteher the bag is currently active or not
                    if belt_activated[i] == True:

                        # checking if the current count is >= the user defined bag limit
                        if total_bag_master[i] >= belt_limit[i]:

                            sio.emit(
                                "limit-stop", {"transaction_id": transaction_id_master[i]})

                            # if the limit has been reached, reset all parameters
                            img_master[i] = np.zeros(
                                (750, 1000, 3), dtype=np.float32)
                            master_ct[i] = CentroidTracker()
                            master_trackableObject[i] = {}
                            total_bag_master[i] = 0
                            label_tag_count_master[i] = 0
                            belt_limit[i] = 0
                            belt_activated[i] = False

                        else:
                            success, img = master_video[i].read()

                            if success:
                                img_master[i] = img
                    else:

                        img_master[i] = np.zeros(
                            (750, 1000, 3), dtype=np.float32)
                        master_ct[i] = CentroidTracker()
                        master_trackableObject[i] = {}
                        total_bag_master[i] = 0
                        label_tag_count_master[i] = 0
                        # belt_limit[i] = 0
                        # belt_activated[i] == False

                if (FRAME_COUNTER % FRAME_SKIP == 0) and (FRAME_COUNTER > AFTER_FRAME):

                    # BAG DETECTION HAPPENING HERE
                    batch_results = detectx(
                        frame_batch=img_master, model=model)

                    # updating rects

                    img_master, rects_master, x_mid = update_rects_plot_bbox(
                        batch_results=batch_results, imgs_rgb=img_master, classes=classes, frame_no=FRAME_COUNTER, transactionid_master=transaction_id_master, beltid_master=beltid_master)

                    master_objectx = []  # [objectsx_1,objectsx_2,objectsx_3,objectsx_4,objectsx_5]

                    for i in range(len(RTSP_LINKS)):
                        # print(f"--------------------------------- vid direction before updating ct_object: {VID_DIRECTION[i]}")
                        master_objectx.append(master_ct[i].update(
                            rects_master[i], x_mid[i], movement_direction=VID_DIRECTION[i]))
                        # master_ct[i] = master_ct[i].update(rects_master[i], x_mid)

                        # bag count happening here but will be updated later after roicount
                        img_master[i], master_trackableObject[i] = tracker_im(
                            img_master[i], objects=master_objectx[i], trackableObject=master_trackableObject[i], movement_direction=VID_DIRECTION[i], ROIX_DISTANCE=roix_master[i])

                    # --------------------------------------------------- WORKING FOR TAG DETECTION --------------------------------------------------------------------------------------

                    id_master = []  # this will store all the ids per image

                    # print(f"------------------------------------ keys: extractig IDS per image ----------------------------")
                    for i in range(len(master_objectx)):

                        id_master.append(tuple(master_objectx[i].keys()))

                    # ----------------------------------------- CREATING BATCH FOR LABEL_TAG DETECTION  and DATA-FLOW TRACKING ---------------------------------------------------------------------

                    # looping through the id_master to create cropped image batch for label detection at once

                    # images will be stored as : {"img_0_5":img_cropped}. '0': img1, "5":ID of the bag
                    img_tag_dict_list = OrderedDict()

                    # z --> if 'z' = 0, that means working with img1 (z=1 --> img2). 0 is the index value we will be using to get objects from ct_master, img_master ,etc
                    for z in range(len(id_master)):

                        movement_direction = VID_DIRECTION[z]
                        # print(f"--------------------------------- vid direction when looping id_master: {VID_DIRECTION[z]}")

                        # ensuring that there are valid bag detections are available
                        if len(id_master[z]) != 0:

                            # ido ---> detected object IDs for a particular image
                            for ido in id_master[z]:

                                tox = master_trackableObject[z].get(
                                    ido, None)  # getting the trackable object

                                centroidx = master_objectx[z].get(
                                    ido, None)  # getting centroid

                                # getting size information of the perticular image
                                image_hx, image_wx, _ = img_master[z].shape

                                # roi_count contains roi values after which all count values (both bag and tag) will be updated

                                # image_wx//2 + ROIX_DISTANCE
                                COUNT_ROIX_L2R = roi_count[z]
                                # image_wx//2 - ROIX_DISTANCE
                                COUNT_ROIX_R2L = roi_count[z]

                                if movement_direction == "left2right":
                                    # this conditions are set to do detetion only inside the designed ROI
                                    if (centroidx[0] <= COUNT_ROIX_L2R) and (not tox.tag_detected) and (tox.counted) and (centroidx[0] > image_wx//2):

                                        # getting BBOx information for this particular ID
                                        xx1, yy1, xx2, yy2 = master_ct[z].BBox.get(
                                            ido, None)

                                        # cropping the image according to BBox values. This will be sent to label tag detetion model
                                        img_crop = img_master[z][yy1:yy2, xx1:xx2]

                                        # storing the cropped image w.r.t img name ond object ID as : {"img_0_5":img_cropped} --->  '0': img1, "5":ID of the bag
                                        img_tag_dict_list[f"img_{z}_{ido}"] = img_crop

                                    elif (centroidx[0] > COUNT_ROIX_L2R) and (tox.tag_detected) and (not tox.tag_crossed_counted):

                                        # print(f"--------------------------------------------------------------------------- inside elif (centroidx[0] > COUNT_ROIX_L2R) and (tox.tag_detected) and (not tox.tag_crossed_counted) ")

                                        # -------------------- increasing bag count
                                        total_bag_master[z] = total_bag_master[z] + 1
                                        # ------------------- increasing label tag count
                                        label_tag_count_master[z] = label_tag_count_master[z] + 1

                                        # API CALLS HERE
                                        sio.emit("tag-entry", {
                                            "belt_id": beltid_master[z],
                                            "transaction_id": transaction_id_master[z],
                                            "is_labeled": True,
                                            "image_location": ""
                                        })
                                        # print(f"bag counting for transaction_id: { transaction_id_master[z]} with belt {beltid_master[z]}: {total_bag_master[z]} and tag:{label_tag_count_master[z]} ")

                                        tox.tag_crossed_counted = True

                                    elif (centroidx[0] > COUNT_ROIX_L2R) and (not tox.tag_detected) and (not tox.tag_crossed_counted):

                                        # -------------------- increasing bag count only
                                        total_bag_master[z] = total_bag_master[z] + 1
                                        # print(f"bag counting for transaction_id: { transaction_id_master[z]} with belt {beltid_master[z]}: {total_bag_master[z]} and tag:{label_tag_count_master[z]} ")

                                        # getting BBOx information for this particular ID
                                        xx1, yy1, xx2, yy2 = master_ct[z].BBox.get(
                                            ido, None)

                                        # cropping the image according to BBox values. This will be sent to label tag detetion model
                                        img_crop = img_master[z][yy1:yy2, xx1:xx2]

                                        tox.tag_crossed_counted = True

                                        image_name = f"{round(time.time() * 1000)}.jpg"
                                        # to save the frame of missed labels
                                        os.makedirs(
                                            f"{MISSED_TAG_PATH_BASE_URL}/missed_tag/{beltid_master[z]}/", exist_ok=True)
                                        crp = Image.fromarray(cv2.cvtColor(
                                            img_crop, cv2.COLOR_BGR2RGB))
                                        crp.save(
                                            f"{MISSED_TAG_PATH_BASE_URL}/missed_tag/{beltid_master[z]}/{image_name}", "JPEG", optimize=True, quality=10)

                                        # API CALLS HERE
                                        sftp.put(
                                            f"{MISSED_TAG_PATH_BASE_URL}/missed_tag/{beltid_master[z]}/{image_name}",  f"{SCP_PATH_BASE_URL}/missed_tag/{beltid_master[z]}/{image_name}")
                                        print("")
                                        sio.emit("tag-entry", {
                                            "belt_id": beltid_master[z],
                                            "transaction_id": transaction_id_master[z],
                                            "is_labeled": False,
                                            "image_location": image_name
                                        })
                                        # print(beltid_master[z], transaction_id_master[z], False, image_name)

                                else:  # moving right2left
                                    # this conditions are set to do detetion only inside the designed ROI
                                    if (centroidx[0] >= COUNT_ROIX_R2L) and (not tox.tag_detected) and (tox.counted) and (centroidx[0] < image_wx//2):

                                        # getting BBOx information for this particular ID
                                        xx1, yy1, xx2, yy2 = master_ct[z].BBox.get(
                                            ido, None)

                                        # cropping the image according to BBox values. This will be sent to label tag detetion model
                                        img_crop = img_master[z][yy1:yy2, xx1:xx2]

                                        # storing the cropped image w.r.t img name ond object ID as : {"img_0_5":img_cropped} --->  '0': img1, "5":ID of the bag
                                        img_tag_dict_list[f"img_{z}_{ido}"] = img_crop

                                    elif (centroidx[0] < COUNT_ROIX_R2L) and (tox.tag_detected) and (not tox.tag_crossed_counted):

                                        # -------------------- increasing bag count
                                        total_bag_master[z] = total_bag_master[z] + 1
                                        # ------------------- increasing label tag count
                                        label_tag_count_master[z] = label_tag_count_master[z] + 1

                                        # API CALLS HERE
                                        sio.emit("tag-entry", {
                                            "belt_id": beltid_master[z],
                                            "transaction_id": transaction_id_master[z],
                                            "is_labeled": True,
                                            "image_location": ""
                                        })
                                        # print(f"bag counting for transaction_id: { transaction_id_master[z]} with belt {beltid_master[z]}: {total_bag_master[z]} and tag:{label_tag_count_master[z]} ")

                                        tox.tag_crossed_counted = True

                                    elif (centroidx[0] < COUNT_ROIX_R2L) and (not tox.tag_detected) and (not tox.tag_crossed_counted):
                                        # -------------------- increasing bag count only
                                        total_bag_master[z] = total_bag_master[z] + 1

                                        # API CALLS HERE
                                        # print(f"bag counting for transaction_id: { transaction_id_master[z]} with belt {beltid_master[z]}: {total_bag_master[z]} and tag:{label_tag_count_master[z]} ")

                                        # getting BBOx information for this particular ID
                                        xx1, yy1, xx2, yy2 = master_ct[z].BBox.get(
                                            ido, None)

                                        # cropping the image according to BBox values. This will be sent to label tag detetion model
                                        img_crop = img_master[z][yy1:yy2, xx1:xx2]

                                        tox.tag_crossed_counted = True

                                        image_name = f"{round(time.time() * 1000)}.jpg"
                                        # to save the frame of missed labels
                                        os.makedirs(
                                            f"{MISSED_TAG_PATH_BASE_URL}/missed_tag/{beltid_master[z]}/", exist_ok=True)
                                        # cv2.imwrite(f"{MISSED_TAG_PATH_BASE_URL}/missed_tag/{beltid_master[z]}/{image_name}",img_crop)
                                        crp = Image.fromarray(cv2.cvtColor(
                                            img_crop, cv2.COLOR_BGR2RGB))
                                        crp.save(
                                            f"{MISSED_TAG_PATH_BASE_URL}/missed_tag/{beltid_master[z]}/{image_name}", "JPEG", optimize=True, quality=10)

                                        # API CALLS HERE
                                        sio.emit("tag-entry", {
                                            "belt_id": beltid_master[z],
                                            "transaction_id": transaction_id_master[z],
                                            "is_labeled": False,
                                            "image_location": image_name
                                        })

                        else:
                            continue  # id no IDs found jump to next loop

                    # print(f"----------------------------------------- img_tag_dict_list:\n :{img_tag_dict_list}")

                    # --------------------------------------------------- LABEL TAG DETECTION --------------------------------------------------------------------

                    # list of all cropped images. i.e. batch of all cropped images which will be sent to label detection model
                    imgesxt = list(img_tag_dict_list.values())
                    # lsit of image_name_id informations  as ["img_0_5","img_2_1"]
                    img_names = list(img_tag_dict_list.keys())

                    # ensures that we are not sending empty batch to the label tag detection model
                    if len(imgesxt) != 0:

                        # TAG DETECTION HAPPENING HERE
                        batch_results_tag = detectx_tag(
                            frame_batch=imgesxt, model=model_tag)

                        # extracting img with label tag bbox ploted on and values ar 'True' or 'False' for label tag detection
                        imgs_results, result_tag_master = label_tag_plot_bbox(
                            batch_results=batch_results_tag, imgs_rgb=imgesxt, classes=model_tag.names, frame_no=FRAME_COUNTER)

                        # -------------------------------------------- UPDATING TRACKERS, COUNT W.R.T IMAGES -------------------------------------------------------------------------------

                        # looping through all the cropped images w.r.t. image and id  extracte from {"img_0_5":img_cropped}
                        for cpo in range(len(img_names)):
                            img_name = img_names[cpo]

                            # if 'z' = 0, that means working with img1 (z=1 --> img2)
                            z = int(img_name.split("_")[1])

                            # getting ID information.
                            ido = int(img_name.split("_")[2])

                            '''
                            - This works as we are looping through all img_names.
                            - If img_names = ["img_0_5","img_0_1", "img_1_3"] ------>  we will be working with the same image img_0 two times and once with img_1 
                            
                            '''

                            # getting tracker

                            tag_value = result_tag_master[cpo]
                            if tag_value:
                                # getting img from img_master list
                                img = img_master[z]
                                # getting tracker for img from trackableObject_master list
                                tracker_t = master_trackableObject[z]

                                # getting the tracker object whose ID = ido
                                to = tracker_t.get(ido, None)

                                xx1, yy1, xx2, yy2 = master_ct[z].BBox.get(
                                    ido, None)  # getting BBox coordinates

                                to.tag_detected = True  # updating the tag_detected value
                                to = tracker_t.get(ido, None)

                                # we are repathcing the cropped image with the original image after label tag detection and bbox plotting
                                img[yy1:yy2, xx1:xx2] = imgs_results[cpo]

                    # ##### ------------------------------- plotting the count results on the frame and saving --------------------------------------------------------------

                    for pl in range(len(img_master)):

                        img_c = img_master[pl]
                        label_countx = label_tag_count_master[pl]
                        total_bag_passed = total_bag_master[pl]
                        x_shape, y_shape = img_c.shape[1], img_c.shape[0]

                        movement_direction = VID_DIRECTION[pl]

                        # x_shape//2 + ROIX_DISTANCE
                        COUNT_ROIX_L2R = roi_count[pl]
                        # x_shape//2 - ROIX_DISTANCE
                        COUNT_ROIX_R2L = roi_count[pl]

                        if movement_direction == "left2right":

                            cv2.line(img_c, (COUNT_ROIX_L2R, 0),
                                     (COUNT_ROIX_L2R, y_shape), (0, 255, 0), 2)

                        else:
                            cv2.line(img_c, (COUNT_ROIX_R2L, 0),
                                     (COUNT_ROIX_R2L, y_shape), (0, 255, 0), 2)

                        cv2.rectangle(img_c, (50, 50),
                                      (950, 240), (10, 10, 10), -1)

                        # cv2.putText(img_c, f"frame no: {FRAME_COUNTER}",(650,100),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)
                        cv2.putText(img_c, f"frinks.ai", (650, 100),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                        cv2.putText(img_c, f"total_bag_passed: {total_bag_passed}", (
                            100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                        cv2.putText(img_c, f"total_bag with_label_tag: {label_countx}", (
                            100, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                        cv2.putText(img_c, f"total_bag without_label_tag: {total_bag_passed-label_countx}", (
                            100, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    # ----------------------------------- to save frames --------------------------------

                    # if SAVE_FRAME:
                    #     for i in range(len(RTSP_LINKS)):
                    #         os.makedirs(f"./detections/all_frames/{transaction_id_master[i]}_{beltid_master[i]}/",exist_ok=True)
                    #         cv2.imwrite(f"./detections/all_frames/{transaction_id_master[i]}_{beltid_master[i]}/{FRAME_COUNTER}.jpg",img_master[i] )

                    # #### saving all videos
                    # if VID_OUT:
                    #     for i in range(len(RTSP_LINKS)):
                    #         video_writer_master[i].write(img_master[i])

                    if IM_SHOW:
                        for i in range(len(RTSP_LINKS)):
                            cv2.imshow(f"{i}", img_master[i])

                    if cv2.waitKey(1) == ord("q"):
                        print(f"[INFO] Exiting. . . ")
                        break

                    LOOP_NO += 1

                    fps = len(RTSP_LINKS) / (time.time() - st)
                    fps_99.append(fps)
                    # print("FPS: %.2f" % fps)
                    if fps_lookup == (100//len(RTSP_LINKS)):
                        avg_fps = np.mean(fps_99)

                        fps_lookup = 1
                        fps_99 = []

                    else:
                        fps_lookup += 1
                    # print(f"\n\n\n----------------------------------- time taken for 1 complete loop: {(time.time() - st)}\n\n\n")

                else:
                    pass

                FRAME_COUNTER += 1

            except Exception as e:

                # print(f"\n\n ----------------------------------------------------------------------------ERROR!!!!!! :\n {e}\n\n")
                print("\n [ERROR] \n ")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                pass

        # if VID_OUT:
        #     for i in range(len(RTSP_LINKS)):
        #         video_writer_master[i].release()

    else:
        print(f"[ERROR!!!] length of all input arrays (len(RTSP_LINKS) == len(vid_directions) == len(roix_master) == len(roi_count) == len(transaction_id_master) == len(beltid_master)) should be same !!! Please give input correctly")

    sftp.close()
# -------------------  calling the main function-------------------------------


main()  # for image
