# -*- coding: utf-8 -*-
"""Copy of product_detector.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1eNTcXl_895SdTDqqVjSiiGY6btZC8_UL
"""

!nvidia-smi

# Commented out IPython magic to ensure Python compatibility.
from google.colab import drive
drive.mount('/gdrive')
# %cd /gdrive/MyDrive/experiment2/

!pip install -q yolov4==2.1.0

from os.path import join, exists
from os import listdir
import json


from global_vars import *
from helpers import load_image_from_link, load_image_from_path
from model import load_normal_models, load_2ndlvl_models
from inference_helpers import *

from primary_image_detector import *

"""## Load Models"""

posenet_model = load_posenet_model()

topwear_models=load_normal_models(topwear)

outerwear_models=load_normal_models(outerwear)
outerwear_models["sub"]["edge_type"]=topwear_models["sub"]["edge_type"]

bottomwear_models=load_normal_models(bottomwear)

footwear_models=load_normal_models(footwear)

overall_models=load_normal_models(overall)

accessories_models=load_normal_models(accessories)

topwear_nonhuman = "topwear_nonhuman"
topwear_nonhuman_model = load_normal_models(topwear_nonhuman)

bottomwear_nonhuman = "bottomwear_nonhuman"
bottomwear_nonhuman_model = load_normal_models(bottomwear_nonhuman)

img = load_image_from_link("https://i.ebayimg.com/images/g/xRYAAOSw~oFXGnNz/s-l400.jpg")
from primary_image_detector import predict_pose
def hasHuman(img, posenet_model):
    lst, image, disp = predict_pose(img, posenet_model)
    lst = sorted(lst, key = lambda x:x[2], reverse=True)
    if (lst[0][2]>0.5) and (lst[1][2]>0.5):
        # print(lst)
        return True
    else:
        # print(lst)
        return False
# hasHuman(img, posenet_model)

topwear_main_model_conf = 0.12
topwear_nonhuman_main_model_conf = 0.12
bottomwear_main_model_conf = 0.65
bottomwear_nonhuman_main_model_conf = 0.65
accessories_main_model_conf = 0.5
footwear_main_model_conf = 0.62

def predict(url, found = None):

    # Image downloading and finding primary image if required
    if type(url) == list:
        img_list = []
        for i in url:
            if type(i)!=str:
                raise Exception("Urls list should contain only string type elements.")
            img_list.append(load_image_from_link(i))
        ind = find_primary(img_list, posenet_model)
        image_link = url[ind]
        img = img_list[ind]
    elif type(url) == str:
        image_link = url
        img = load_image_from_link(url)
    else:
        raise Exception("Url parameter should be string type or a list of string type.")
    #check if it has human or not
    # hash = hasHuman(img, posenet_model)
    # print(hash)
    hash = True

    # initialising all the variables
    topwear_detection = []
    bottomwear_detection = []
    accessories_sub_detection = {}
    footwear_detection = []

    bottomwear_sub_detection={}
    topwear_sub_detection={}
    overall_sub_detection={}
    outerwear_sub_detection={}

    # resolving the already known thing
    if hash:
        if found == None:
            topwear_detection, topwear_color = topwear_nonhuman_model["main"].predict(img, 0.1, topwear_nonhuman_main_model_conf)
            bottomwear_detection, bottomwear_color = bottomwear_nonhuman_model["main"].predict(img, 0.1, bottomwear_nonhuman_main_model_conf)
            accessories_sub_detection = accessories_prediction(img, accessories_models['main'], ren, 0.1, accessories_main_model_conf)
            footwear_detection, footwear_color = footwear_models["main"].predict(img, 0.1, footwear_main_model_conf)
        elif found in topwear_models["main"].class_dict.values():
            topwear_detection = [[found, 1]]
        elif found == topwear:
            topwear_detection, topwear_color = topwear_nonhuman_model["main"].predict(img, 0.1, topwear_nonhuman_main_model_conf)
        elif found in bottomwear_models["main"].class_dict.values():
            bottomwear_detection = [[found, 1]]
        elif found == bottomwear:
            bottomwear_detection, bottomwear_color = bottomwear_nonhuman_model["main"].predict(img, 0.1, bottomwear_nonhuman_main_model_conf)
        elif (found == accessories) or (found in accessories_models["main"].class_dict.values()):
            accessories_sub_detection = accessories_prediction(img, accessories_models['main'], ren, 0.1, accessories_main_model_conf)
        elif (found == footwear) or (found in footwear_models["main"].class_dict.values()):
            footwear_detection, footwear_color = footwear_models["main"].predict(img, 0.1, footwear_main_model_conf)
        else:
            raise Exception(found+" not found in any model.")
    else:
        if found == None:
            topwear_detection, topwear_color = topwear_models["main"].predict(img, 0.1, topwear_main_model_conf)
            bottomwear_detection, bottomwear_color = bottomwear_models["main"].predict(img, 0.1, bottomwear_main_model_conf)
            accessories_sub_detection = accessories_prediction(img, accessories_models['main'], ren, 0.1, accessories_main_model_conf)
            footwear_detection, footwear_color = footwear_models["main"].predict(img, 0.1, footwear_main_model_conf)
        elif found in topwear_models["main"].class_dict.values():
            topwear_detection = [[found, 1]]
        elif found == topwear:
            topwear_detection, topwear_color = topwear_models["main"].predict(img, 0.1, topwear_main_model_conf)
        elif found in bottomwear_models["main"].class_dict.values():
            bottomwear_detection = [[found, 1]]
        elif found == bottomwear:
            bottomwear_detection, bottomwear_color = bottomwear_models["main"].predict(img, 0.1, bottomwear_main_model_conf)
        elif (found == accessories) or (found in accessories_models["main"].class_dict.values()):
            accessories_sub_detection = accessories_prediction(img, accessories_models['main'], ren, 0.1, accessories_main_model_conf)
        elif (found == footwear) or (found in footwear_models["main"].class_dict.values()):
            footwear_detection, footwear_color = footwear_models["main"].predict(img, 0.1, footwear_main_model_conf)
        else:
            raise Exception(found+" not found in any model.")

    # making further predictions
    if len(topwear_detection)!=0:
        topwear_detection = [topwear_detection[0]]
        if topwear_detection[0][0] in ['bodysuit', 'jumpsuit', 'kaftan', 'dress']:
            if (len(bottomwear_detection)==0) or (topwear_detection[0][1]>bottomwear_detection[0][1]):
                overall_sub_detection = sub_model_prediction(img, topwear_detection, overall_models['sub'], 0.1, 0.1)
            else:topwear_detection = []
        elif topwear_detection[0][0] in ['blazers', 'cardigan', 'coat', 'jacket']:
            outerwear_sub_detection = sub_model_prediction(img, topwear_detection, outerwear_models['sub'], 0.1, 0.1)
        else:
            topwear_sub_detection = sub_model_prediction(img, topwear_detection, topwear_models['sub'], 0.1, 0.1)

    bottomwear_sub_detection = sub_model_prediction(img, bottomwear_detection, bottomwear_models['sub'], 0.1, 0.1)

    footwear_sub_detection = sub_model_prediction(img, footwear_detection, footwear_models['sub'], 0.1, 0.1)
    if len(footwear_detection)!=0:
        footwear_sub_detection['color']=transform_color(footwear_color)

    # transforming results
    trans_result = transform_result({
                    topwear:topwear_sub_detection,
                    bottomwear:bottomwear_sub_detection,
                    overall:overall_sub_detection,
                    outerwear:outerwear_sub_detection,
                    footwear:footwear_sub_detection,
                    accessories:accessories_sub_detection
                },ren)
    trans_result["found_primary"] = image_link
    return trans_result

"""# Updated Way to Run DB Images"""

from PIL.Image import fromarray as fa
from time import sleep
from IPython.display import clear_output
import json
import urllib.error

topwearClasses = ['shirts', 'sweatshirt', 'tops', 'poncho', 'brasserie']
outerwearClasses = ['blazers', 'coat', 'jacket', 'cardigan']
overallClasses = ['bodysuit', 'dress', 'jumpsuit', 'kaftan']

f = open("/gdrive/MyDrive/experiment2/grroomTagging/db_image_data/filtered/split/Input_filename.txt")
d = f.read()
f.close()
d = json.loads(d)

updated = []
first_how_many = 20000
data = d[len(updated):first_how_many]
count = len(updated)
for i in data[:]:
    print(count)
    url = i["image"]
    id = i["_id"]
    img = load_image_from_link(url)
    width, height, _ = img.shape
    display(fa(img).resize((int(400*height/width), 400)))
    cls = list(topwear_models['main'].class_dict.values())
    cls.extend(list(bottomwear_models['main'].class_dict.values()))
    cls.extend(list(footwear_models['main'].class_dict.values()))
    for cnt in range(0, len(cls), 4):
        try:
            s = str(cnt)+ "."+" "+cls[cnt]
            print(s.ljust(25, " "), end = "")
            s = str(cnt+1)+ "."+" "+cls[cnt+1]
            print(s.ljust(25, " "), end = "")
            s = str(cnt+2)+ "."+" "+cls[cnt+2]
            print(s.ljust(25, " "), end = "")
            s = str(cnt+3)+ "."+" "+cls[cnt+3]
            print(s.ljust(25, " "))
        except:
            break
    sleep(0.7)
    inp = input("choose what all are there in the image?(For example, 1,13,6,7): -\n")
    inp = list(map(int, inp.split(',')))
    inp = list(set([cls[k] for k in inp]))
    clear_output()

    result = {}
    topwearPresent = [False,None]
    overallPresent = [False,None]
    outerwearPresent = [False,None]
    bottomwearPresent = [False,None]
    footwearPresent = [False,None]
    for k in inp:
        if k in outerwearClasses:outerwearPresent = [True, k]
        if k in topwearClasses:topwearPresent = [True, k]
        if k in overallClasses:overallPresent = [True, k]
        if k in bottomwear_models["main"].class_dict.values():bottomwearPresent = [True, k]
        if k in footwear_models["main"].class_dict.values():footwearPresent = [True,k]
    
    if outerwearPresent[0]:
        tmp = predict(url, outerwearPresent[1])
        result[outerwear] = tmp[outerwear]
        result[topwear] = tmp[topwear]
        if topwearPresent[0]:result[topwear]["type"] = [ren[topwear]["Type"]['prediction'][topwearPresent[1]]]
        elif overallPresent[0]:result["overalls"]["type"] = [overallPresent[1]]
        else:result[topwear] = {}
    elif topwearPresent[0]:
        tmp = predict(url, topwearPresent[1])
        result[topwear] = tmp[topwear]
    elif overallPresent[0]:
        tmp = predict(url, overallPresent[1])
        result["overalls"] = tmp["overalls"]
    if bottomwearPresent[0]:
        tmp = predict(url, bottomwearPresent[1])
        result[bottomwear] = tmp[bottomwear]
    if footwearPresent[0]:
        tmp = predict(url, footwearPresent[1])
        if "footwearType" in tmp[footwear].keys():
            del tmp[footwear]["footwearType"]
        result[footwear] = tmp[footwear]
        # print(tmp[footwear])
        if result[footwear] == {}:
            result[footwear]={"type":[ren[footwear]["Type"]['prediction'][footwearPresent[1]]]}
        else:
            result[footwear]["type"]=[ren[footwear]["Type"]['prediction'][footwearPresent[1]]]
    result["_id"] = id
    result["image"] = url
    updated.append(result)
    count+=1
    
    for j in result.keys():
        print(j)
        try:
            for k in result[j].keys():
                print(" "*5,k.ljust(20), result[j][k])
        except:
            print(" "*5,result[j])
    if input("Hit enter to continue:\n") == 'n':
        clear_output()
        continue
    clear_output()

"""#Saving the data"""

f = open("/gdrive/MyDrive/experiment2/grroomTagging/db_image_data/filtered/processed/Output_filename.txt", "w") #change
f.write(json.dumps(updated))
f.close()