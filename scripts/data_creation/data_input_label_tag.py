import json

deepak_data = [{"VID_OUT":None, ### givr video path
                "SAVE_FRAME":False, ### true or false
                 "IM_SHOW": False, ### true or false
                 "FRAME_SKIP": 1,
                 "ROIX_DISTANCE":500,

                 "DETECT_ONLY_AFTER_CX":0,
                 "DETECT_ONLY_AFTER_CY":0,


                 "SCORE_THRESHOLD_BAG":0.5,
                 "IOU_THRESHOLD_BAG":0.3,

                 "SCORE_THRESHOLD_TAG":0.1,
                 "IOU_THRESHOLD_TAG":0.3,

                 "BAG_MODEL_WEIGHT":"bag_800dt_coco_epoch130.pt",
                 "TAG_MODEL_WEIGHT":"tag_1135dt_coco_best.pt"

                 }]

outfile = open("/home/frinks1/Downloads/DP/bag_deployment_code/label_bag_tag/model_files/model_parameters.json", "w")
json.dump(deepak_data,outfile,indent= 2)
outfile.close()

data_jsonx = json.load(open("/home/frinks1/Downloads/DP/bag_deployment_code/label_bag_tag/model_files/model_parameters.json",))
print(data_jsonx[0]['SCORE_THRESHOLD_BAG'])