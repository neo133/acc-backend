import json

deepak_data = [{"VID_OUT":None, ### givr video path
                "SAVE_FRAME":False, ### true or false
                 "IM_SHOW": False, ### true or false
                 "FRAME_SKIP": 1,
                #  "ROIX_DISTANCE":500,

                 "DETECT_ONLY_AFTER_CX":0,
                 "DETECT_ONLY_AFTER_CY":0,


                 "SCORE_THRESHOLD_BAG":0.7,
                 "IOU_THRESHOLD_BAG":0.15,

                 "SCORE_THRESHOLD_TAG":0.5,
                 "IOU_THRESHOLD_TAG":0.15,

                 "BAG_MODEL_WEIGHT":"bag_835_coco_epoch170.pt",
                 "TAG_MODEL_WEIGHT":"tag_513_coco_best.pt",

                 ################# RTSP LINKS from belts
                 "b1":["/home/frinks1/Downloads/DP/Heidelberg/label_tag/test/unseen_clips/102_clip.mp4",0,1500,1900], ### [rtsp links, direction, roix, roicount]
                 "b2":["/home/frinks1/Downloads/DP/ACC_NEW/data/testing/split2_00000003755000000.mp4",1,700,500],
                 "b3":["/home/frinks1/Downloads/DP/Heidelberg/label_tag/test/unseen_clips/115_clip.mp4",0,1500,1900],
                 "b4":["/home/frinks1/Downloads/DP/Heidelberg/label_tag/test/unseen_clips/377a_clip.mp4",1,700,500],
                 "b5":["/home/frinks1/Downloads/DP/Heidelberg/label_tag/test/unseen_clips/401a_clip.mp4",1,700,500],

                 }]

outfile = open("/home/frinks1/Downloads/DP/bag_deployment_new_rules_static/label_bag_tag/model_files/model_parameters.json", "w")
json.dump(deepak_data,outfile,indent= 2)
outfile.close()

data_jsonx = json.load(open("/home/frinks1/Downloads/DP/bag_deployment_new_rules_static/label_bag_tag/model_files/model_parameters.json",))
print(data_jsonx[0]['SCORE_THRESHOLD_BAG'])