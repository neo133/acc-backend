import json

deepak_data = [{"VID_OUT": None,  # givr video path
                "SAVE_FRAME": False,  # true or false
                "IM_SHOW": True,  # true or false
                "FRAME_SKIP": 1,
                #  "ROIX_DISTANCE":0,

                "DETECT_ONLY_AFTER_CX": 0,
                "DETECT_ONLY_AFTER_CY": 0,


                "SCORE_THRESHOLD_BAG": 0.7,
                "IOU_THRESHOLD_BAG": 0.15,

                "BAG_MODEL_WEIGHT": "bestm_bag.pt",


                # RTSP LINKS from belts
                # [rtsp links, direction, roix]
                "1": ["/home/frinks1/Downloads/DP/Heidelberg/bag_counting/video/1/hiv00004.mp4", 1, 700],
                "2":["/home/frinks1/Downloads/DP/Heidelberg/bag_counting/video/1/hiv00021.mp4", 1, 700],
                #  "3":["/home/frinks1/Downloads/DP/Heidelberg/bag_counting/video/1/hiv00022_reversed.mp4",0,1700],
                #  "b4":["/home/frinks1/Downloads/DP/Heidelberg/bag_counting/video/1/hiv00040.mp4",0,700],
                #  "b5":["/home/frinks1/Downloads/DP/Heidelberg/bag_counting/video/1/hiv00074.mp4",0,700],
                }]

outfile = open(
    "/home/frinks1/Documents/acc/acc-backend/scripts/bag_counting/model_files/model_parameters.json", "w")
json.dump(deepak_data, outfile, indent=2)
outfile.close()

data_jsonx = json.load(open(
    "/home/frinks1/Documents/acc/acc-backend/scripts/bag_counting/model_files/model_parameters.json",))
print(data_jsonx[0]['SCORE_THRESHOLD_BAG'])
