import json

deepak_data = [{"VID_OUT":None, ### givr video path
                "SAVE_FRAME":False, ### true or false
                 "IM_SHOW": False, ### true or false
                 "FRAME_SKIP": 1,
                 "ROIX_DISTANCE":0,

                 "DETECT_ONLY_AFTER_CX":0,
                 "DETECT_ONLY_AFTER_CY":0,


                 "SCORE_THRESHOLD_BAG":0.6,
                 "IOU_THRESHOLD_BAG":0.3,

                 "BAG_MODEL_WEIGHT":"1088dt_coco_epoch220.pt"

                 }]

outfile = open("/home/frinks1/Downloads/DP/bag_deployment_code/bag_counting/model_files/model_parameters.json", "w")
json.dump(deepak_data,outfile,indent= 2)
outfile.close()

data_jsonx = json.load(open("/home/frinks1/Downloads/DP/bag_deployment_code/bag_counting/model_files/model_parameters.json",))
print(data_jsonx[0]['SCORE_THRESHOLD_BAG'])
