
### importing required libraries

# from re import T
import torch
import cv2  
import time
import numpy as np
import os
import sys
# import argparse

#### trackers
from mylib.centroidtracker_move import CentroidTracker
from mylib.trackableobject import TrackableObject

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
# ROIX_DISTANCE = data_jsonx['ROIX_DISTANCE'] ### a ROI is created at a distance of 500 pxl away from centroid. Count information will be updated when a bag crosses this ROI

DETECT_ONLY_AFTER_CX = data_jsonx['DETECT_ONLY_AFTER_CX'] ## 245
DETECT_ONLY_AFTER_CY = data_jsonx['DETECT_ONLY_AFTER_CY']

DIRECTION_DICT = {0:"left2right", 1:"right2left"}

SCORE_THRESHOLD_BAG = data_jsonx['SCORE_THRESHOLD_BAG']
IOU_THRESHOLD_BAG = data_jsonx['IOU_THRESHOLD_BAG'] 

BAG_MODEL_WEIGHT = f"./model_files/{data_jsonx['BAG_MODEL_WEIGHT']}" ### BAG_MODEL_WEIGHT = '/home/frinks1/Downloads/DP/Heidelberg/bag_counting/yolov5l_training_results/training_backup_1088_data_640ims_coco_customhype_adam_video247_WITHOUTSBH/weights/epoch220.pt' ### best weight at 267 BEST RESULT SO FAR at epoch220



###### reading information about the belt 
BELT_MASTER = ['b1','b2','b3','b4','b5']
B1_LINK, B1_DIR, B1_ROIX = data_jsonx["b1"]
B2_LINK, B2_DIR, B2_ROIX = data_jsonx["b2"]
B3_LINK, B3_DIR, B3_ROIX = data_jsonx["b3"]
B4_LINK, B4_DIR, B4_ROIX = data_jsonx["b4"]
B5_LINK, B5_DIR, B5_ROIX = data_jsonx["b5"]

################








# print(f"[INFO] ---------------- MODEL PARAMETERS ARE: ----------------------\n")
# print(f"VID_OUT = {VID_OUT}, \nSAVE_FRAME = {SAVE_FRAME}, \nIM_SHOW = {IM_SHOW}, \nFRAME_SKIP = {FRAME_SKIP}, \nROIX_DISTANCE = {ROIX_DISTANCE}, \nDETECT_ONLY_AFTER_CX = {DETECT_ONLY_AFTER_CX}, \nDETECT_ONLY_AFTER_CY = {DETECT_ONLY_AFTER_CY}, \nSCORE_THRESHOLD_BAG = {SCORE_THRESHOLD_BAG}, \nIOU_THRESHOLD_BAG = {IOU_THRESHOLD_BAG}, \nBAG_MODEL_WEIGHT = {BAG_MODEL_WEIGHT}")


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
def update_rects_plot_bbox(batch_results,imgs_rgb,classes,frame_no,transactionid_master, beltid_master):

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

        frame_forsave = frame.copy() ### to save the raw frame without any annotation on it if the threshold of any detected obect is < threshold value


        ### looping through the detections per image
        for i in range(n):
            row = cord[i]
            print(f"SCORE_THRESHOLD_BAG:{SCORE_THRESHOLD_BAG}")
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
    
                        cv2.putText(frame, text_d + f" {round(float(row[4]),2)}", (x1, y1-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(255,255,255), 2)
                        # cv2.putText(frame, text_d , (x1, y1-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(255,255,255), 2)  ### no probability


                        rects.append((x1,y1,x2,y2))
            
            
            ### code to save frames less than threshold
            
            elif (row[4] < SCORE_THRESHOLD_BAG) and (0.4< row[4] ):

                x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape) ## BBOx coordniates
                width = x2 - x1
                height = y2 - y1

                area = width * height

                if area > 300000:  #### this is to filter out detections with very small area (like small portion of the bag is visible at corner of the screen)
                    print(f"row[4]: {row[4]}")
                    ### saving frames with detection below threshold values
                    os.makedirs(f"./detections/less_th_bag/",exist_ok=True)
                    cv2.imwrite(f"./detections/less_th_bag/{transactionid_master[im]}_{beltid_master[im]}_f{frame_no}_dn{n}_th{round(float(row[4]),5)}.jpg",frame_forsave )

        
        
        imgs_results.append(frame)
        rects_master.append(rects)

    return imgs_results, rects_master, x_mid

############# --------------------------------------------------------- tracker function -------------------------------------------------------

def tracker_im(frame,objects,trackableObject,movement_direction, bag_count,ROIX_DISTANCE, transactionid, beltid):
    # print(f"[INFO] Tracking and counting. . . ")

    image_h, image_w, _ = frame.shape
    # print(f"--------------------------------- vid direction inside tracker_im: {movement_direction}")


    # loop through the tracked objects
    for (objectID, centroid) in objects.items():

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
                    if centroid[0] >  ROIX_DISTANCE:  ### ROIX_DISTANCE will be used if you want to create an alternet counting line instead of the central line 
                        bag_count += 1

                        ##### API CALLS HERE 

                        print(f"bag counting for transaction_id: { transactionid} with belt {beltid} is: {bag_count} ")

                        to.counted = True


                else: ### moving right2left
                    if centroid[0] <  ROIX_DISTANCE:  # ### custom ROI to do counting, image_w//2: is ideal condition
                        bag_count += 1

                        ### API CALLS HERE

                        print(f"bag counting for transaction_id: { transactionid} with belt {beltid} is: {bag_count} ")


                        to.counted = True

        # store the trackable object inside the dictionary
        trackableObject[objectID] = to

        # draw the ID of the object and centroid of the object on the output frame
        ob_id = "ID {}".format(objectID)
        # cv2.putText(frame, ob_id,(centroid[0] - 10, centroid[1] - 10),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0, 255), 2)
        # cv2.putText(frame, f"{(centroid[0], centroid[1])}",(centroid[0] - 50, centroid[1] - 50),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0, 255), 2)
        cv2.circle(frame, (centroid[0], centroid[1]), 5, (255, 0, 0), -1)


    
    return frame, trackableObject, bag_count


### ------------------------------------------------------------------ Main function ---------------------------------------------------------------------------------------------------

def main(): ##img_path = Full path to image


    ###### USER inputs 
    RTSP_LINKS = [B1_LINK,B2_LINK,B3_LINK,B4_LINK,B5_LINK]
    vid_directions = [B1_DIR, B2_DIR, B3_DIR, B4_DIR, B5_DIR]
    roix_master = [B1_ROIX, B2_ROIX, B3_ROIX, B4_ROIX, B5_ROIX]
    transaction_id_master = ["id1","id2","id3","id4","id5"]
    beltid_master = BELT_MASTER

    socket_value = "b2"
    execute_loop = True ### controls the main while loop
    stop_buffer = True ### to control the buffer loop when there is no shipment input
    belt_activated = [False,False,False,False,False]
    belt_limit = [3,5,30,10,10]



    ## checking that len of all input arrays should be same
    len_check = True
    try:
        assert len(RTSP_LINKS) == len(vid_directions) == len(roix_master) ==  len(transaction_id_master) == len(beltid_master)
    except:
        len_check = False



    if len_check: ### len(RTSP_LINKS) == len(vid_directions): ## len of all input arrays should be same

        VID_DIRECTION = [DIRECTION_DICT[i] for i in vid_directions]
        


        try:
            print(f"\n[INFO] Loading model... ")
            ## loading the custom trained model
            # model =  torch.hub.load('ultralytics/yolov5', 'custom', path='bestm_label_bag.pt',force_reload=True) ## if you want to download the git repo and then run the detection
            model =  torch.hub.load('./yolov5-master', 'custom', source ='local', path=BAG_MODEL_WEIGHT,force_reload=True) ### lastm_label_bag.pt--good result,  The repo is stored locally
            # model.conf = SCORE_THRESHOLD_BAG ### setting up confidence threshold
            model.iou = IOU_THRESHOLD_BAG ## setting up iou threshold

            classes = model.names ### class names in string format
        
        except Exception as e:
            
            # print(f"\n\n ----------------------------------------------------------------------------ERROR!!!!!! :\n {e}\n\n")
            print(f"\n[ERROR] Failed to load model!!! Please check the model path. Exiting... \n ")

            sys.exit(1) ### exiting

        
        # #### to create windows according to the no. of videos in RTSP links
        if IM_SHOW:
            for i in range(len(RTSP_LINKS)):
                cv2.namedWindow(f'{i}', cv2.WINDOW_NORMAL)

            
            

                        
                    

        # ############## ------------------------------------------------------ TRACKERS --------------------------------------------------------------------

        master_ct=[]  #### [ct_label_1,ct_label_2,ct_label_3,ct_label_4,ct_label_5]
        master_trackableObject = []   ### [trackableObject_label_1, trackableObject_label_2 ,trackableObject_label_3, trackableObject_label_4, trackableObject_label_5]
        total_bag_master = []  ### [0,0,0,0,0]



        ### creating different objects for each and every videos in the RTSP link
        for i in range(len(RTSP_LINKS)):
            master_ct.append(CentroidTracker())
            master_trackableObject.append({})
            total_bag_master.append(0)


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
        #         fps = 20  # int(vid.get(cv2.CAP_PROP_FPS))
        #         codec = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        #         out1 = cv2.VideoWriter(f"{VID_OUT}/{vw}_bag.mp4", codec, fps, (width, height))

        #         video_writer_master.append(out1)



    

    ##########--------------------------------------- fps parameters ----------------------------------------------------  


        LOOP_NO = 1
        fps_lookup = 1
        fps_99 =[]

        detection_time =[]
        detection_tracker_time = []

        FRAME_COUNTER = 1




    ############ -------------------------------- main while loop for looping through the videos ------------------------------

        ### this buffer loop as we need to run the programe in every cases. i.e. even if there is no shipment input,the programme will be looping here and will move to the main loop after getting the shipment details
        while not execute_loop:
            if stop_buffer == True:
                print(f"[INFO] Stopping buffer loop and starting main loop.")
                execute_loop = True
            continue


        print(f"[INFO] Working with video link ... ")

        while execute_loop:

            try:

                print(f"--------------------------- {FRAME_COUNTER} ----------------------------")

                st = time.time()

                #### this list contains frames from all the videos i.e. image batch creaded by combining the frames from all the videos
                img_master=[np.zeros((750,1000, 3), dtype=np.float32),np.zeros((750,1000, 3), dtype=np.float32),np.zeros((750,1000, 3), dtype=np.float32),np.zeros((750,1000, 3), dtype=np.float32),np.zeros((750,1000, 3), dtype=np.float32)]   ### [img1,img1,img1,img1,img1] ----> frame 1 from all videos 

                
                ### checking socket values
                if socket_value in beltid_master:
                    
                    index_value = beltid_master.index(socket_value)

                    belt_activated[index_value] = True

                

                
                ##### checking if the bag count crossed the counting limit for the particular bag
                for i in range(len(RTSP_LINKS)):

                    if belt_activated[i] == True: ### first we area checking.. wheteher the bag is currently active or not



                        if total_bag_master[i] >= belt_limit[i]:

                            img_master[i] = np.zeros((750,1000, 3), dtype=np.float32)
                            master_ct[i] = CentroidTracker()
                            master_trackableObject[i] = {}
                            total_bag_master[i] = 0
                            belt_limit[i] = 0
                            belt_activated[i] == False
                            socket_value="z"
                        
                        else:
                            success, img = master_video[i].read()
                        
                            if success:
                                img_master[i] = img

                
                # if socket_value =="z":
                #     socket_value = "b1"

                # if FRAME_COUNTER >= 130:
                #     socket_value = "b4"

                # if FRAME_COUNTER >= 170:
                #     socket_value = "b2"
                #     belt_limit[1] = 5

                # if FRAME_COUNTER >= 190:
                #     socket_value = "b3"

                # if FRAME_COUNTER >= 200:
                #     socket_value = "b5"
                # # if FRAME_COUNTER >= 205:
                # #     socket_value = "b2"


                




                

                if (FRAME_COUNTER%FRAME_SKIP ==0) and (FRAME_COUNTER >AFTER_FRAME):

                    batch_results = detectx(frame_batch=img_master, model = model) ### BAG DETECTION HAPPENING HERE 

                    img_master, rects_master, x_mid = update_rects_plot_bbox(batch_results=batch_results, imgs_rgb = img_master, classes= classes, frame_no= FRAME_COUNTER, transactionid_master= transaction_id_master,beltid_master = beltid_master)


                    master_objectx = []  #### [objectsx_1,objectsx_2,objectsx_3,objectsx_4,objectsx_5]

                    for i in range(len(RTSP_LINKS)):

                        # print(master_ct[i].update)
                        # print(f"--------------------------------- vid direction before updating ct_object: {VID_DIRECTION[i]}")
                        master_objectx.append(master_ct[i].update(rects_master[i], x_mid[i], movement_direction = VID_DIRECTION[i]))
                        # master_ct[i] = master_ct[i].update(rects_master[i], x_mid)

                        ### bag counting is happening here 
                        img_master[i],master_trackableObject[i],total_bag_master[i] = tracker_im(img_master[i],objects = master_objectx[i],trackableObject =master_trackableObject[i], movement_direction= VID_DIRECTION[i], bag_count= total_bag_master[i],ROIX_DISTANCE = roix_master[i], transactionid=transaction_id_master[i], beltid = beltid_master[i] )





                    # ##### ------------------------------- plotting the count results on the frame and saving --------------------------------------------------------------
                    
                    for pl in range(len(img_master)):
                        
                        img_c  = img_master[pl]
                        # label_countx = label_tag_count_master[pl]
                        total_bag_passed = total_bag_master[pl] 
                        x_shape, y_shape =img_c.shape[1],img_c.shape[0]

                        movement_direction = VID_DIRECTION[pl]

                        COUNT_ROIX_L2R =  roix_master[pl]
                        COUNT_ROIX_R2L =  roix_master[pl]

                        if movement_direction == "left2right":
                            
                            cv2.line(img_c, (COUNT_ROIX_L2R, 0),(COUNT_ROIX_L2R, y_shape), (0, 255, 0), 2) ######## counting line

                        else:
                            cv2.line(img_c, (COUNT_ROIX_R2L, 0),(COUNT_ROIX_R2L, y_shape), (0, 255, 0), 2)



                        # cv2.line(img_c, (x_shape//2, 0),(x_shape//2, y_shape), (0, 255, 255), 2) ######## center line  , , image_w = x_shape, image_h= y_shape


                        cv2.rectangle(img_c, (50,50),(950,130), (10,10,10), -1)
            
                        cv2.putText(img_c, f"frame no: {FRAME_COUNTER}",(650,100),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)
                        cv2.putText(img_c , f"total_bag_passed: {total_bag_passed}", (100,100), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,0), 2)

                        print(f"total_bag_passed:{total_bag_passed}")               
                        

                    ###### ----------------------------------- to save frames --------------------------------           
                    
                    # if SAVE_FRAME:
                    #     for i in range(len(RTSP_LINKS)):
                    #         os.makedirs(f"./detections/vid_{i}/",exist_ok=True)
                    #         cv2.imwrite(f"./detections/vid_{i}/{FRAME_COUNTER}.jpg",img_master[i] )


                    #### saving all videos
                    # if VID_OUT:
                    #     for i in range(len(RTSP_LINKS)):
                    #         video_writer_master[i].write(img_master[i])


                    if IM_SHOW:
                        for i in range(len(RTSP_LINKS)):
                            cv2.imshow(f"{i}",img_master[i])

                    
                    if cv2.waitKey(1)== ord("q"):
                        print(f"[INFO] Exiting. . . ")
                        break

                    LOOP_NO+=1


                    fps = len(RTSP_LINKS) / (time.time() - st)
                    fps_99.append(fps)
                    # print("FPS: %.2f" % fps)
                    if fps_lookup == (100//len(RTSP_LINKS)):
                        avg_fps = np.mean(fps_99)
                        # print(f"\n\n\n-------------------------------------------------------------->>>>> AVG_FPS_{fps_lookup}: %.2f" % avg_fps, "\n\n\n")
                        fps_lookup =1
                        fps_99 = []
                        # print(f"fps_99: {fps_99}")

                    else:
                        fps_lookup +=1
                    print(f"\n\n\n----------------------------------- time taken for 1 complete loop: {(time.time() - st)}\n\n\n")


                
                else:
                    # print(f"skipping as current frame is : {FRAME_COUNTER}")
                    pass
                    
                FRAME_COUNTER+=1

            except Exception as e:
                
                # print(f"\n\n ----------------------------------------------------------------------------ERROR!!!!!! :\n {e}\n\n")
                print(f"\n[ERROR]... \n ")

                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                pass

        print('[INFO] Task completed. Exiting..')

        # if VID_OUT:
        #     for i in range(len(RTSP_LINKS)):
        #         video_writer_master[i].release()

    else:
        print(f"[ERROR!!!] the vid_list, dir_list and roix_list should be of equal length !!! Please give input correctly")


### -------------------  calling the main function-------------------------------
main() 
            

