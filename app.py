import csv
import argparse
from PIL import Image
from flask import Flask, render_template, send_file, request


app = Flask(__name__)

frame = -1
filenames = ['frame_1.jpg', 'frame_271.jpg', 'frame_272.jpg']
mot_data = {}

# Define the route for the home page
@app.route('/')
def home():
    # Load the background image
    img_filename = filenames[frame]
    bg_image = Image.open(f"sample_images/{img_filename}")

    # Pass the image dimensions to the template
    bg_width, bg_height = bg_image.size

    # Render the template with the image dimensions
    return render_template('index.html', img_filename=img_filename, bg_width=bg_width, bg_height=bg_height)


@app.route('/next_image')
def next_image():
    global frame

    frame += 1
    if frame >= len(filenames):
        frame = len(filenames) - 1
    return send_file(f"sample_images/{filenames[frame]}", mimetype='image/jpeg')


@app.route('/prev_image')
def prev_image():
    global frame

    frame -= 1
    if frame < 0:
        frame = 0
    return send_file(f"sample_images/{filenames[frame]}", mimetype='image/jpeg')


@app.route('/get_current_frame_data')
def get_current_frame_data():
    return {"frame": frame,
            "squares": mot_data[frame]}



@app.route('/get_image', methods=["POST"])
def get_image():
    data = request.get_json()
    frame = data["frame"]

    if frame < 0:
        frame = 0
    elif frame >= len(filenames):
        frame = len(filenames) - 1

    return send_file(f"sample_images/{filenames[frame]}", mimetype='image/jpeg')


@app.route('/save_square', methods=["POST"])
def save_squares():
    try:
        data = request.get_json()
        filename = data["filename"]
        squares = data["squares"]
        print(squares)
        with open(filename, "a+") as f:
            f.write(squares)
        return { 
            "status": "success",
            "msg": "Data added"
        }
    except Exception as e:
        return { 
            "status": "failure",
             "msg": str(e) 
        }


def load_mot_data(filename: str):
    mot_data = {}
    with open(filename) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            frame, id, bb_left, bb_top, bb_width, bb_height, _, _, _, _ = map(float, row)
            frame = frame - 1
            if frame not in mot_data:
                mot_data[frame] = []
            mot_data[frame].append({
                "id": id, "bb_left": bb_left, "bb_top": bb_top, 
                "bb_width": bb_width, "bb_height": bb_height})
    return mot_data

if __name__ == '__main__':
    # create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Flask app that lets the user fix partial tracking annotations")
    parser.add_argument('-f', '--filename', type=str, 
                        help='Name of the file with the partial detections (MOT format)')
    args = parser.parse_args()

    if args.filename is not None:
        mot_data = load_mot_data(args.filename)
        print(mot_data)

    app.run(debug=True)
