from flask import Flask, render_template, send_file, request, url_for
from PIL import Image

app = Flask(__name__)

frame = -1
filenames = ['frame_1.jpg', 'frame_271.jpg', 'frame_272.jpg']

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


if __name__ == '__main__':
    app.run(debug=True)
