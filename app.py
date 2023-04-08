import os
import re
import csv
import argparse
from PIL import Image
from flask import Flask, render_template, send_file, request

from typing import *

try:
    import sift
    import cv2
    CAN_USE_SIFT = 1
except ModuleNotFoundError:
    print("SIFT dependencies not match. Skipping")
    CAN_USE_SIFT = 0


app = Flask(__name__)

frame = -1
image_files = ['sample_images/frame_1.jpg',
               'sample_images/frame_271.jpg', 'sample_images/frame_272.jpg']
mot_data = {}

# Define the route for the home page


@app.route('/')
def home():
    # Load the background image
    img_filename = image_files[frame]
    bg_image = Image.open(img_filename)

    # Pass the image dimensions to the template
    bg_width, bg_height = bg_image.size

    # Render the template with the image dimensions
    return render_template('index.html', CAN_USE_SIFT=CAN_USE_SIFT, 
                           frame_count=len(image_files),
                           img_filename=img_filename,
                           bg_width=bg_width, bg_height=bg_height)


@app.route('/next_image')
def next_image():
    global frame

    frame += 1
    if frame >= len(image_files):
        frame = len(image_files) - 1
    return send_file(image_files[frame], mimetype='image/jpeg')


@app.route('/prev_image')
def prev_image():
    global frame

    frame -= 1
    if frame < 0:
        frame = 0
    return send_file(image_files[frame], mimetype='image/jpeg')


@app.route('/get_current_frame_data', methods=['POST'])
def get_current_frame_data():
    global mot_data

    data = request.get_json()
    use_sift = data["use_sift"]

    if frame not in mot_data:
        mot_data[frame] = []

    if not use_sift or frame == 0:
        return {"frame": frame,
                "squares": mot_data[frame]}

    else:
        data = []
        for obj in mot_data[frame - 1]:
            next_obj = find_object_with_id(frame, obj["id"])
            
            prev_image = cv2.imread(image_files[frame - 1])
            curr_image = cv2.imread(image_files[frame])
            if not next_obj:
                print(frame, obj["id"], "obj not found")
                # search around for object
                bbx, bby = obj["bb_left"] - 30, obj["bb_top"] - 30
                if bbx < 0: bbx = 0
                if bby < 0: bby = 0
                pnext_obj = {"id": obj["id"], 
                            "bb_left": bbx, "bb_top": bby,
                            "bb_width": obj["bb_width"] + 30, 
                            "bb_height": obj["bb_height"] + 30}
                
                res = sift.find_perimeter(
                    prev_image, curr_image, obj, pnext_obj)
            else:
                res = sift.find_perimeter(
                    prev_image, curr_image, obj, next_obj)
            
            if res is not None:
                x, y, w, h = res
                data.append({"id": obj["id"], "bb_left": x, "bb_top": y,
                            "bb_width": w, "bb_height": h})
                print(f"Added obj {obj['id']} on frame {frame}")
            
            # no matches found but we managed to get some detection
            else:
                print(frame, obj["id"], None)
                if next_obj:
                    data.append(next_obj)

        return {"frame": frame, "squares": data}


@app.route('/get_image', methods=["POST"])
def get_image():
    global frame

    data = request.get_json()
    frame = data["frame"]

    if frame < 0:
        frame = 0
    elif frame >= len(image_files):
        frame = len(image_files) - 1

    return send_file(image_files[frame], mimetype='image/jpeg')


@app.route('/save_square', methods=["POST"])
def save_squares():
    try:
        data = request.get_json()
        squares = data["squares"]
        print(squares)
        with open(save_filename, "w") as f:
            f.write(squares)
        return {
            "status": "success",
            "msg": f"Frame {frame} data added"
        }
    except Exception as e:
        return {
            "status": "failure",
            "msg": str(e)
        }


def find_object_with_id(frame: int, id: int) -> Dict[str, float]:
    for obj in mot_data[frame]:
        if obj["id"] == id:
            return obj
    return {}


def load_mot_data(filename: str):
    mot_data = {}

    with open(filename) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            frame, id, bb_left, bb_top, bb_width, bb_height, _, _, _, _ = map(
                float, row)
            frame = frame - 1

            if frame not in mot_data:
                mot_data[frame] = []

            mot_data[frame].append({
                "id": id, "bb_left": bb_left, "bb_top": bb_top,
                "bb_width": bb_width, "bb_height": bb_height})

    return mot_data


def get_image_filepaths(folderpath: str) -> List[str]:

    def natural_keys(text):
        '''
        alist.sort(key=natural_keys) sorts in human order
        http://nedbatchelder.com/blog/200712/human_sorting.html
        (See Toothy's implementation in the comments)
        '''
        return [int(c) if c.isdigit() else c
                for c in re.split(r'(\d+)', text)]
    filenames = [os.path.join(folderpath, filename)
                 for filename in os.listdir(folderpath)]

    filenames.sort(key=natural_keys)
    return filenames


if __name__ == '__main__':
    # create an ArgumentParser object
    parser = argparse.ArgumentParser(
        description="Flask app that lets the user fix partial tracking annotations")
    parser.add_argument('-m', '--mot_file', type=str,
                        help='Name of the file with the partial detections (MOT format)')
    parser.add_argument('-i', '--images', type=str,
                        help="Folder containing the images related to the MOT file. The images must be \
                            in the format *_d.{png/jpg}")
    parser.add_argument('-n', '--save_name', type=str, default="mot.txt",
                        help='Name to save the mot file')
    args = parser.parse_args()

    if args.mot_file is not None:
        mot_data = load_mot_data(args.mot_file)

    image_files = get_image_filepaths(args.images)
    save_filename = args.save_name

    app.run(debug=True)
