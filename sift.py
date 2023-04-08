#%%
import cv2
import math
import numpy as np
import matplotlib.pyplot as plt

from typing import *


sift = cv2.SIFT_create()
bf = cv2.BFMatcher()


def get_image(path: str) -> np.ndarray:
    return cv2.imread(path)



def find_perimeter(prev_image: np.ndarray, curr_image: np.ndarray, 
                   prev_obj: Dict[str, float], curr_obj: Dict[str, float],
                   offset_x=30, offset_y=30, pad_results=True,
                   log_err = False) -> \
                        "Tuple[float, float, float, float] | None":
    """Increases the detection box of the current frame and performs SIFT
    template matching"""
    tx, ty, tw, th = int(prev_obj["bb_left"]), int(prev_obj["bb_top"]), \
        int(prev_obj["bb_width"]), int(prev_obj["bb_height"])

    target = prev_image[ty: ty+th, tx: tx+tw]

    x, y, w, h = curr_obj["bb_left"], curr_obj["bb_top"], \
        curr_obj["bb_width"], curr_obj["bb_height"]
    x1, y1 = int(x) - offset_x, int(y) - offset_y
    if x1 < 0: x1 = 0
    if y1 < 0: y1 = 0

    x2, y2 = int(x) + int(w) + offset_x, int(y) + int(h) + offset_y
    res = find_rect(target, curr_image[y1:y2, x1:x2], log_err=log_err)
    if res is None: return res

    ntx, nty, ntw, nth = res
    if pad_results:
        ntx -= 5
        nty -= 5
        ntw += 5
        nth += 5
        if ntx < 0: ntx = 0
        if nty < 0: nty = 0
    
    return x1 + ntx, y1 + nty, ntw, nth


def find_rect(target: np.ndarray, image: np.ndarray, log_err=False) -> \
        "Tuple[float, float, float, float] | None":
    target_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
    target_keypoints, target_descriptors = sift.detectAndCompute(target_gray, None)
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_keypoints, image_descriptors = sift.detectAndCompute(image_gray, None)

    matches = bf.knnMatch(target_descriptors,image_descriptors,k=2)
    try:
        good = [m for m,n in matches if m.distance < 0.75*n.distance]
        
        query_pts = np.float32(
            [target_keypoints[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        
        train_pts = np.float32(
            [image_keypoints[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        
        # finding  perspective transformation between two planes
        matrix, mask = cv2.findHomography(query_pts, train_pts, cv2.RANSAC, 5.0)
        # initializing height and width of the image
        h, w, _ = target.shape

        # saving all points in pts
        pts = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
        
        # applying perspective algorithm
        dst = cv2.perspectiveTransform(pts, matrix)
        
        x, y = dst[0,0,0], dst[0,0,1]
        w, h = dst[2,0,0] - x, dst[2,0,1] - y
        return (x, y, w, h)
    
    # the may fail if no good points are found or if matches doesn't return two points
    except Exception as e:
        if log_err: print(e) 
        return None


#%%
if __name__ == "__main__":
    img71 = cv2.imread("images/city_above_images/frame_71.jpg")
    img72 = cv2.imread("images/city_above_images/frame_72.jpg")
    with open("mots/city_above_mot.txt") as f:
        mot_data = [[int(math.floor(float(n))) for n in line.split(",")]
                    for line in f.readlines()]
        mot_data71 = [d for d in mot_data if d[0]==71]
        mot_data72 = [d for d in mot_data if d[0]==72]

    i = -1
    x1, y1 = mot_data71[i][2] + 2, mot_data71[i][3] + 4
    x2, y2 = mot_data71[i][2] + mot_data71[i][4] - 2, mot_data71[i][3] + mot_data71[i][5] - 2

    prev_obj = {"bb_left": x1, "bb_top": y1,
                "bb_width": x2 - x1, "bb_height": y2 - y1}
    car = img71[y1:y2, x1:x2]
    i = -2

    x1, y1 = mot_data72[i][2] - 30, mot_data72[i][3] - 30
    x2, y2 = mot_data72[i][2] + mot_data72[i][4] + 30, mot_data72[i][3] + mot_data72[i][5] + 30

    curr_obj = {"bb_left": x1 + 30, "bb_top": y1 + 30,
                "bb_width": x2 - x1 - 30, "bb_height": y2 - y1 - 30}
    car3 = img72[y1:y2, x1:x2]

    x, y, w, h = find_perimeter(img71, img72, prev_obj, curr_obj)
    #x, y, w, h = find_rect(car, car3)
    plt.imshow(cv2.rectangle(img72.copy(), (int(x), int(y)), (int(x+w), int(y+h)), (0,0,0), 5))


# %%
