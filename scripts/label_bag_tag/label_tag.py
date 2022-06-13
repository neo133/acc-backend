
### importing required libraries

from tarfile import TarFile
import torch
import cv2
import time
import numpy as np
import os
import sys
import argparse

#### trackers
from mylib.centroidtracker_move import CentroidTracker
from mylib.trackableobject_delaysolved import TrackableObject
from collections import OrderedDict

import json


############ --------------   GLOBAL VARIABLES   ---------------------

print("[INFO] Reading json file and loading model parameters")

### reading parameter json file
data_jsonx = json.load(open("./model_files/model_parameters.json",))
data_jsonx = data_jsonx[0]


VID_OUT = data_jsonx['VID_OUT'] ## "./detections"
SAVE_FRAME = data_jsonx['SAVE_FRAME']
IM_SHOW = data_jsonx['IM_SHOW']

FRAME_SKIP = data_jsonx['FRAME_SKIP']
AFTER_FRAME =1 # 1350 ## 3500
ROIX_DISTANCE = data_jsonx['ROIX_DISTANCE'] ### a ROI is created at a distance of 500 pxl away from centroid. Count information will be updated when a bag crosses this ROI

DETECT_ONLY_AFTER_CX = data_jsonx['DETECT_ONLY_AFTER_CX'] ## 245
DETECT_ONLY_AFTER_CY = data_jsonx['DETECT_ONLY_AFTER_CY']

DIRECTION_DICT = {0:"left2right", 1:"right2left"}

SCORE_THRESHOLD_BAG = data_jsonx['SCORE_THRESHOLD_BAG']
SCORE_THRESHOLD_TAG = data_jsonx['SCORE_THRESHOLD_TAG']
IOU_THRESHOLD_BAG = data_jsonx['IOU_THRESHOLD_BAG'] 
IOU_THRESHOLD_TAG = data_jsonx['IOU_THRESHOLD_TAG']


BAG_MODEL_WEIGHT = f"./model_files/{data_jsonx['BAG_MODEL_WEIGHT']}" ### BAG_MODEL_WEIGHT = '/home/frinks1/Downloads/DP/Heidelberg/label_bag/yolov5l_training_results/training_backup_800_data_640ims_COCO_ADAM_cstmHyp_hJsw/weights/epoch130.pt'
TAG_MODEL_WEIGHT = f"./model_files/{data_jsonx['TAG_MODEL_WEIGHT']}"  ### TAG_MODEL_WEIGHT = '/home/frinks1/Downloads/DP/Heidelberg/label_tag/yolov5l_training_results_data/training_backup_1135dt_coco_hype_adam_hJsw/weights/best.pt'

print(f"[INFO] ---------------- MODEL PARAMETERS ARE: ----------------------\n")
print(f"VID_OUT = {VID_OUT}, \nSAVE_FRAME = {SAVE_FRAME}, \nIM_SHOW = {IM_SHOW}, \nFRAME_SKIP = {FRAME_SKIP}, \nROIX_DISTANCE = {ROIX_DISTANCE}, \nDETECT_ONLY_AFTER_CX = {DETECT_ONLY_AFTER_CX}, \nDETECT_ONLY_AFTER_CY = {DETECT_ONLY_AFTER_CY}, \nSCORE_THRESHOLD_BAG = {SCORE_THRESHOLD_BAG}, \nIOU_THRESHOLD_BAG = {IOU_THRESHOLD_BAG}, \nSCORE_THRESHOLD_TAG = {SCORE_THRESHOLD_TAG},\nIOU_THRESHOLD_TAG = {IOU_THRESHOLD_TAG}, \nBAG_MODEL_WEIGHT = {BAG_MODEL_WEIGHT} ,\nTAG_MODEL_WEIGHT{TAG_MODEL_WEIGHT}")




### -------------------------------------- function to run detection ---------------------------------------------------------
def detectx (frame_batch, model):

    results = model(frame_batch, augment=True)

    ### loopting through detections w.r.t image in order to create the final result_file

    batch_results = []

    for ir in range(len(results)):

        labels, cordinates = results.xyxyn[ir][:, -1], results.xyxyn[ir][:, :-1]

        batch_results.append((labels,cordinates))



    return batch_results

### ------------------------------------ to plot the BBox and results --------------------------------------------------------
def update_rects_plot_bbox(batch_results,imgs_rgb,classes):

    """
    --> This function takes results, frame and classes
    --> results: contains labels and coordinates predicted by model on the given frame
    --> classes: contains the strting labels

    """

    imgs_results=[]
    rects_master = []
    x_mid = []
    
    for im in range(len(imgs_rgb)):   

        
        frame = imgs_rgb[im]
        labels, cord = batch_results[im]
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        x_mid.append(x_shape//2)

        
        rects =[] ### rects per image

        ### looping through the detections per image
        for i in range(n):
            row = cord[i]
            if row[4] >= SCORE_THRESHOLD_BAG: ### threshold value for detection. We are discarding everything below this value
                # print(f"[INFO] Extracting BBox coordinates. . . ")
                x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape) ## BBOx coordniates
                # startX, startY, endX, endY = x1,y1,x2,y2
                text_d = classes[int(labels[i])]

                cx = int((x1+x2)/2.0)
                cy = int((y1+y2)/2.0)


                if text_d == 'cement_bag':

                    # print(f"----------- centroid before passing value for tracking: (cx,cy) ---> {(cx,cy)}")
                    if (cx> DETECT_ONLY_AFTER_CX) :#and (cy>DETECT_ONLY_AFTER_CY): #### to filter out wrong detection on person moving in the background


                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2) ## BBox
                        

                            
                        # cv2.putText(frame, text_d + f" {round(float(row[4]),2)}", (x1, y1-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(255,255,255), 2)

                        cv2.putText(frame, text_d, (x1, y1-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(255,255,255), 2) ## without probability


                        rects.append((x1,y1,x2,y2))


        imgs_results.append(frame)
        rects_master.append(rects)

    return imgs_results, rects_master, x_mid

############# --------------------------------------------------------- tracker function -------------------------------------------------------

def tracker_im(frame,objects,trackableObject,movement_direction):
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
                    if centroid[0] > image_w//2: 

                        to.counted = True


                else: ### moving right2left
                    if centroid[0] < image_w//2: 

                        to.counted = True

        # store the trackable object inside the dictionary
        trackableObject[objectID] = to

        # draw the ID of the object and centroid of the object on the output frame
        ob_id = "ID {}".format(objectID)
        # cv2.putText(frame, ob_id,(centroid[0] - 10, centroid[1] - 10),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0, 255), 2)
        # cv2.putText(frame, f"{(centroid[0], centroid[1])}",(centroid[0] - 50, centroid[1] - 50),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0, 255), 2)
        cv2.circle(frame, (centroid[0], centroid[1]), 5, (255, 0, 0), -1)


    
    return frame, trackableObject



### ------------------------------------ to plot the BBox and result of LABEL TAG--------------------------------------------------------
def label_tag_plot_bbox(batch_results,imgs_rgb,classes):

    """
    --> This function takes results, frame and classes
    --> results: contains labels and coordinates predicted by model on the given frame
    --> classes: contains the strting labels

    """
    # print(imgs_rgb)
    imgs_results=[]
    result_tag_master = []

    
    for im in range(len(imgs_rgb)):
        # image_h, image_w, _ = frame.shape
        
        
        frame = imgs_rgb[im]
        labels, cord = batch_results[im]
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]



        # print(f"[INFO] Total {n} tag detections. . . ")
        # print(f"[INFO] Looping through all detections. . . ")


        if n !=0:
            ### looping through the detections per image
            for i in range(n):
                row = cord[i]
                if row[4] >= SCORE_THRESHOLD_TAG: ### threshold value for detection. We are discarding everything below this value
                    # print(f"[INFO] Extracting BBox coordinates. . . ")
                    x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape) ## BBOx coordniates
                    # startX, startY, endX, endY = x1,y1,x2,y2
                    text_d = classes[int(labels[i])]


                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255,0), 2) ## BBox 
                    # cv2.putText(frame, text_d + f" {round(float(row[4]),2)}", (x1, y1-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,0,0), 2)
                    # cv2.putText(frame, text_d + f" {round(float(row[4]),2)}", (x1-80, y1-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,0,0), 2)

                    cv2.putText(frame, text_d , (x1-80, y1-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,0,0), 2) #### without probability 




            imgs_results.append(frame)
            result_tag_master.append(True)
        else:
            imgs_results.append(frame)
            result_tag_master.append(False)


    return imgs_results, result_tag_master




### ------------------------------------------------------------------ Main function ---------------------------------------------------------------------------------------------------

def main(): ##img_path = Full path to image


    ##### to get inputs from commandline
    cli = argparse.ArgumentParser()

    cli.add_argument("--vid_list", nargs ="*", type= str, default= []) ### list of video directories 
    cli.add_argument("--dir_list", nargs ="*", type= int, default= []) ## list of moving directions


    args = cli.parse_args() ### parsing the arguments

    RTSP_LINKS = args.vid_list
    vid_directions = args.dir_list


    if len(RTSP_LINKS) == len(vid_directions):

        VID_DIRECTION = [DIRECTION_DICT[i] for i in vid_directions]




        try:
            print(f"[INFO] Loading model... ")
            ## loading the custom trained model
            # model =  torch.hub.load('ultralytics/yolov5', 'custom', path='bestm_label_bag.pt',force_reload=True) ## if you want to download the git repo and then run the detection
            model =  torch.hub.load('./yolov5-master', 'custom', source ='local', path=BAG_MODEL_WEIGHT,force_reload=True) ### lastm_label_bag.pt--good result,  The repo is stored locally
            model.conf = SCORE_THRESHOLD_BAG ### setting up confidence threshold
            model.iou = IOU_THRESHOLD_BAG ## setting up iou threshold

            classes = model.names ### class names in string format


            ### tag detection model 
            model_tag =  torch.hub.load('./yolov5-master', 'custom', source ='local', path=TAG_MODEL_WEIGHT,force_reload=True) ### The repo is stored locally
            model_tag.conf = SCORE_THRESHOLD_TAG ### setting up confidence threshold
            model_tag.iou = IOU_THRESHOLD_TAG ## setting up iou threshold


        except Exception as e:
            
            # print(f"\n\n ----------------------------------------------------------------------------ERROR!!!!!! :\n {e}\n\n")
            print(f"\n[ERROR] Failed to load model!!! Please check the model path. Exiting... \n ")

            sys.exit(1) ### exiting


        
        #### to create windows according to the no. of videos in RTSP links
        # if IM_SHOW:
        #     for i in range(len(RTSP_LINKS)):
        #         cv2.namedWindow(f'{i}', cv2.WINDOW_NORMAL)

            
            

                        
                    

        ############## ------------------------------------------------------ TRACKERS --------------------------------------------------------------------

        master_ct=[]  #### [ct_label_1,ct_label_2,ct_label_3,ct_label_4,ct_label_5]
        master_trackableObject = []   ### [trackableObject_label_1, trackableObject_label_2 ,trackableObject_label_3, trackableObject_label_4, trackableObject_label_5]
        label_tag_count_master = []  ### [0,0,0,0,0]
        total_bag_master = []  ### [0,0,0,0,0]



        ### creating different objects for each and every videos in the RTSP link
        for i in range(len(RTSP_LINKS)):
            master_ct.append(CentroidTracker())
            master_trackableObject.append({})
            label_tag_count_master.append(0)
            total_bag_master.append(0)



        # print(type(master_ct[0]), '----------------------this is master ct--------------------')




        ########-------------------------------------------------- readnig frames directly from videos --------------------------------------------------------------
        master_video = []  #### [video1 ,video2,video3,video4,video5]

        

        for i in range(len(RTSP_LINKS)):

            master_video.append(cv2.VideoCapture(RTSP_LINKS[i]))

        ### CREATING VIDEO WRITERS TO SAVE VIDEO
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

        


        ##########--------------------------------------- fps parameters ----------------------------------------------------  


        LOOP_NO = 1
        fps_lookup = 1
        fps_99 =[]

        detection_time =[]
        detection_tracker_time = []

        FRAME_COUNTER = 1




        ############ -------------------------------- main while loop for looping through the videos ------------------------------

        print(f"[INFO] working with videos . . . ")


        while True:

            try:
                # print(f"--------------------------------------------------------------- WORKING WITH FRAME: {FRAME_COUNTER} --------------------------------------------- ")
                st = time.time()

                #### this list contains frames from all the videos i.e. image batch creaded by combining the frames from all the videos              

                img_master=[]   ### [img1,img1,img1,img1,img1] ----> frame 1 from all videos 

                for i in range(len(RTSP_LINKS)):
                    success, img = master_video[i].read()
                    if not success:
                        img = np.zeros((750,1000, 3), dtype=np.float32)
                    img_master.append(img)

                

                if (FRAME_COUNTER%FRAME_SKIP ==0) and (FRAME_COUNTER >AFTER_FRAME):


                    batch_results = detectx(frame_batch=img_master, model = model) ### BAG DETECTION HAPPENING HERE 

                    ### updating rects 

                    img_master, rects_master, x_mid = update_rects_plot_bbox(batch_results=batch_results, imgs_rgb = img_master, classes= classes)

                    master_objectx = []  #### [objectsx_1,objectsx_2,objectsx_3,objectsx_4,objectsx_5]

                    for i in range(len(RTSP_LINKS)):
                        # print(f"--------------------------------- vid direction before updating ct_object: {VID_DIRECTION[i]}")
                        master_objectx.append(master_ct[i].update(rects_master[i], x_mid[i], movement_direction = VID_DIRECTION[i]))
                        # master_ct[i] = master_ct[i].update(rects_master[i], x_mid)
                        img_master[i],master_trackableObject[i] = tracker_im(img_master[i],objects = master_objectx[i],trackableObject =master_trackableObject[i], movement_direction= VID_DIRECTION[i] )






                    ##### --------------------------------------------------- WORKING FOR TAG DETECTION --------------------------------------------------------------------------------------

                    id_master = [] ### this will store all the ids per image


                    # print(f"------------------------------------ keys: extractig IDS per image ----------------------------")
                    for i in range(len(master_objectx)):
                    
                        id_master.append(tuple(master_objectx[i].keys()))



                    ####### ----------------------------------------- CREATING BATCH FOR LABEL_TAG DETECTION  and DATA-FLOW TRACKING ---------------------------------------------------------------------

                    #### looping through the id_master to create cropped image batch for label detection at once 

                    img_tag_dict_list = OrderedDict() #### images will be stored as : {"img_0_5":img_cropped}. '0': img1, "5":ID of the bag


                    for z in range(len(id_master)): ### z --> if 'z' = 0, that means working with img1 (z=1 --> img2). 0 is the index value we will be using to get objects from ct_master, img_master ,etc

                        movement_direction = VID_DIRECTION[z]
                        # print(f"--------------------------------- vid direction when looping id_master: {VID_DIRECTION[z]}")


                        if len(id_master[z]) != 0 : ## ensuring that there are valid bag detections are available

                            for ido in id_master[z]: ## ido ---> IDs for a particular image

                                tox = master_trackableObject[z].get(ido, None)  ### getting the trackable object 

                                centroidx = master_objectx[z].get(ido, None) ## getting centroid 

                                image_hx, image_wx, _ = img_master[z].shape ### getting size information of the perticular image

                                COUNT_ROIX_L2R = image_wx//2 + ROIX_DISTANCE
                                COUNT_ROIX_R2L = image_wx//2 - ROIX_DISTANCE


                                if movement_direction == "left2right":
                                    if (centroidx[0] <= COUNT_ROIX_L2R) and (not tox.tag_detected) and (tox.counted) and (centroidx[0] > image_wx//2 ): ### this conditions are set to do detetion only inside the designed ROI

                                        xx1,yy1, xx2,yy2 = master_ct[z].BBox.get(ido, None) ### getting BBOx information for this particular ID


                                        img_crop = img_master[z][yy1:yy2, xx1:xx2] ### cropping the image according to BBox values. This will be sent to label tag detetion model


                                        

                                        img_tag_dict_list[f"img_{z}_{ido}"]= img_crop ### storing the cropped image w.r.t img name ond object ID as : {"img_0_5":img_cropped} --->  '0': img1, "5":ID of the bag


                                    elif (centroidx[0] > COUNT_ROIX_L2R) and (tox.tag_detected) and (not tox.tag_crossed_counted):

                                        # print(f"--------------------------------------------------------------------------- inside elif (centroidx[0] > COUNT_ROIX_L2R) and (tox.tag_detected) and (not tox.tag_crossed_counted) ")
                                        
                                        total_bag_master[z]  = total_bag_master[z] +1  ### -------------------- increasing bag count
                                        label_tag_count_master[z] = label_tag_count_master[z] +1 #### ------------------- increasing label tag count
                                        tox.tag_crossed_counted = True

                                    elif (centroidx[0] > COUNT_ROIX_L2R) and (not tox.tag_detected)  and (not tox.tag_crossed_counted):                                       

                                        total_bag_master[z]  = total_bag_master[z] +1 ### -------------------- increasing bag count only
                                        tox.tag_crossed_counted = True

                                        ### to save the frame of missed labels
                                        # cv2.imwrite(f"./detections/missed_tag.jpg",img_master[z])




                                else: #### moving right2left
                                    if (centroidx[0] >= COUNT_ROIX_R2L) and (not tox.tag_detected) and (tox.counted) and (centroidx[0] < image_wx//2 ): ### this conditions are set to do detetion only inside the designed ROI

                                        xx1,yy1, xx2,yy2 = master_ct[z].BBox.get(ido, None) ### getting BBOx information for this particular ID


                                        img_crop = img_master[z][yy1:yy2, xx1:xx2] ### cropping the image according to BBox values. This will be sent to label tag detetion model

                                        img_tag_dict_list[f"img_{z}_{ido}"]= img_crop ### storing the cropped image w.r.t img name ond object ID as : {"img_0_5":img_cropped} --->  '0': img1, "5":ID of the bag

                                    elif (centroidx[0] < COUNT_ROIX_R2L) and (tox.tag_detected) and (not tox.tag_crossed_counted):
                                        
                                        total_bag_master[z]  = total_bag_master[z] +1  ### -------------------- increasing bag count
                                        label_tag_count_master[z] = label_tag_count_master[z] +1 #### ------------------- increasing label tag count
                                        tox.tag_crossed_counted = True

                                    elif (centroidx[0] < COUNT_ROIX_R2L) and (not tox.tag_detected)  and (not tox.tag_crossed_counted):
                                        total_bag_master[z]  = total_bag_master[z] +1  ### -------------------- increasing bag count only
                                        tox.tag_crossed_counted = True

                                        ### to save the frame of missed labels
                                        # cv2.imwrite(f"./detections/missed_tag.jpg",img_master[z])

                        else:
                            continue ### id no IDs found jump to next loop


                    
                    # print(f"----------------------------------------- img_tag_dict_list:\n :{img_tag_dict_list}")


                    ###### --------------------------------------------------- LABEL TAG DETECTION and COUNT VALUES UPDATION --------------------------------------------------------------------


                    imgesxt = list(img_tag_dict_list.values()) #### list of all cropped images. i.e. batch of all cropped images which will be sent to label detection model
                    img_names = list(img_tag_dict_list.keys()) ### lsit of image_name_id informations  as ["img_0_5","img_2_1"]



                    if len(imgesxt) !=0: ### ensures that we are not sending empty batch to the label tag detection model

                        batch_results_tag = detectx(frame_batch=imgesxt, model = model_tag) ### TAG DETECTION HAPPENING HERE 

                        #### extracting img with label tag bbox ploted on and values ar 'True' or 'False' for label tag detection
                        imgs_results, result_tag_master = label_tag_plot_bbox(batch_results= batch_results_tag , imgs_rgb = imgesxt,classes= model_tag.names)




                        ###### -------------------------------------------- UPDATING TRACKERS, COUNT W.R.T IMAGES -------------------------------------------------------------------------------


                        for cpo in range(len(img_names)):  ### looping through all the cropped images w.r.t. image and id  extracte from {"img_0_5":img_cropped} 
                            img_name = img_names[cpo]

                            z= int(img_name.split("_")[1])  ### if 'z' = 0, that means working with img1 (z=1 --> img2)

                            ido= int(img_name.split("_")[2]) ### getting ID information. 


                            '''
                            - This works as we are looping through all img_names.
                            - If img_names = ["img_0_5","img_0_1", "img_1_3"] ------>  we will be working with the same image img_0 two times and once with img_1 
                            
                            '''


                            #### getting tracker 

                            tag_value = result_tag_master[cpo]
                            if tag_value:
                                img = img_master[z] ### getting img from img_master list
                                tracker_t = master_trackableObject[z] ## getting tracker for img from trackableObject_master list

                                to = tracker_t.get(ido, None) ### getting the tracker object whose ID = ido

                                xx1,yy1, xx2,yy2 = master_ct[z].BBox.get(ido, None) ### getting BBox coordinates


                                to.tag_detected = True ### updating the tag_detected value
                                to = tracker_t.get(ido, None)




                                img[yy1:yy2, xx1:xx2] = imgs_results[cpo] #### we are repathcing the cropped image with the original image after label tag detection and bbox plotting
                                


                    # ##### ------------------------------- plotting the count results on the frame and saving --------------------------------------------------------------
                    
                    for pl in range(len(img_master)):
                        
                        img_c  = img_master[pl]
                        label_countx = label_tag_count_master[pl]
                        total_bag_passed = total_bag_master[pl] 
                        x_shape, y_shape =img_c.shape[1],img_c.shape[0]

                        movement_direction = VID_DIRECTION[pl]

                        COUNT_ROIX_L2R = x_shape//2 + ROIX_DISTANCE
                        COUNT_ROIX_R2L = x_shape//2 - ROIX_DISTANCE

                        if movement_direction == "left2right":
                            
                            cv2.line(img_c, (COUNT_ROIX_L2R, 0),(COUNT_ROIX_L2R, y_shape), (0, 255, 0), 2) ######## 

                        else:
                            cv2.line(img_c, (COUNT_ROIX_R2L, 0),(COUNT_ROIX_R2L, y_shape), (0, 255, 0), 2)


                        cv2.rectangle(img_c, (50,50),(950,240), (10,10,10), -1)
            
                        # cv2.putText(img_c, f"frame no: {FRAME_COUNTER}",(650,100),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)
                        cv2.putText(img_c, f"frinks.ai",(650,100),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)
                        cv2.putText(img_c , f"total_bag_passed: {total_bag_passed}", (100,100), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,0), 2)                    
                        cv2.putText(img_c , f"total_bag with_label_tag: {label_countx}", (100,150), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,0), 2)
                        cv2.putText(img_c , f"total_bag without_label_tag: {total_bag_passed-label_countx}", (100,200), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255), 2)

                    
                    
                    
                    
                    
                    ###### ----------------------------------- to save frames --------------------------------           
                    
                    # if SAVE_FRAME:
                    #     for i in range(len(RTSP_LINKS)):
                    #         os.makedirs(f"./detections/vid_{i}/",exist_ok=True)
                    #         cv2.imwrite(f"./detections/vid_{i}/{FRAME_COUNTER}.jpg",img_master[i] )



                    # #### saving all videos
                    # if VID_OUT:
                    #     for i in range(len(RTSP_LINKS)):
                    #         video_writer_master[i].write(img_master[i])


                    # if IM_SHOW:
                    #     for i in range(len(RTSP_LINKS)):
                    #         cv2.imshow(f"{i}",img_master[i])


                    
                    # if cv2.waitKey(1)== ord("q"):
                    #     print(f"[INFO] Exiting. . . ")
                    #     break

                    LOOP_NO+=1


                    fps = len(RTSP_LINKS) / (time.time() - st)
                    fps_99.append(fps)
                    # print("FPS: %.2f" % fps)
                    if fps_lookup == (100//len(RTSP_LINKS)):
                        avg_fps = np.mean(fps_99)

                        fps_lookup =1
                        fps_99 = []

                    else:
                        fps_lookup +=1
                    # print(f"\n\n\n----------------------------------- time taken for 1 complete loop: {(time.time() - st)}\n\n\n")

                
                else:
                    pass
                    
                FRAME_COUNTER+=1

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
        print(f"[ERROR!!!] the vid_list and dir_list should be of equal length !!! Please give input correctly")

### -------------------  calling the main function-------------------------------


main() ## for image
            
