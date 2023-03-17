from flask import Flask, render_template
from PIL import Image

app = Flask(__name__)

# Define the route for the home page
@app.route('/')
def home():
    # Load the background image
    img_filename = 'frame_1.jpg'
    bg_image = Image.open(f"static/{img_filename}")

    # Pass the image dimensions to the template
    bg_width, bg_height = bg_image.size

    # Render the template with the image dimensions
    return render_template('index.html', img_filename=img_filename, bg_width=bg_width, bg_height=bg_height)


if __name__ == '__main__':
    app.run(debug=True)
