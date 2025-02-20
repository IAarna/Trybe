import os
import logging
from flask import Flask, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename
from PIL import Image
from dataset import validate_selection  # Import validation function

app = Flask(__name__)

# Folders
UPLOAD_FOLDER = "static/uploads"
CLOTHES_FOLDER = "static/clothes"
DUMMY_MODEL = "static/dummy/image.png"

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CLOTHES_FOLDER, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/result", methods=["GET"])
def result():
    return render_template("result.html")

@app.route("/upload-face", methods=["POST"])
def upload_face():
    file = request.files.get("image")
    if not file:
        logging.error("No image uploaded in request")
        return jsonify({"error": "No image uploaded!"}), 400

    filename = secure_filename(file.filename)
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(image_path)
    
    absolute_url = url_for('static', filename=f'uploads/{filename}', _external=True)
    logging.info(f"Face uploaded successfully: {absolute_url}")
    return jsonify({"message": "Face uploaded successfully!", "image_path": absolute_url})

@app.route("/apply-clothing", methods=["POST"])
def apply_clothing():
    data = request.json
    image_path = data.get("image_path")
    tshirt_filename = data.get("tshirt")
    body_shape = data.get("body_shape")
    size = data.get("size")

    if not all([image_path, tshirt_filename, body_shape, size]):
        logging.error("Missing input data in request")
        return jsonify({"error": "Invalid input data!"}), 400

    # Validate body shape and size
    is_valid, message = validate_selection(body_shape, size)
    if not is_valid:
        logging.error(f"Validation failed: {message}")
        return jsonify({"error": message}), 400

    # Convert URL to local path if necessary
    if image_path.startswith("http"):
        # Extract the filename from the URL
        base_url = url_for('static', filename='', _external=True)  # e.g., http://127.0.0.1:5000/static/
        relative_path = image_path.replace(base_url, "static/")
        image_path = relative_path
        logging.info(f"Converted URL to local path: {image_path}")

    tshirt_path = os.path.join(CLOTHES_FOLDER, tshirt_filename)
    output_path = os.path.join(UPLOAD_FOLDER, "output.png")

    # Check if all required files exist
    if not os.path.exists(image_path):
        logging.error(f"User face image not found: {image_path}")
        return jsonify({"error": "User face image not found!"}), 400
    if not os.path.exists(tshirt_path):
        logging.error(f"T-shirt image not found: {tshirt_path}")
        return jsonify({"error": "T-shirt image not found!"}), 400
    if not os.path.exists(DUMMY_MODEL):
        logging.error(f"Dummy model image not found: {DUMMY_MODEL}")
        return jsonify({"error": "Dummy model image not found!"}), 400

    try:
        # Load images
        user_face = Image.open(image_path).convert("RGBA")
        tshirt_img = Image.open(tshirt_path).convert("RGBA")
        dummy_model = Image.open(DUMMY_MODEL).convert("RGBA")

        # Resize dummy model based on body shape and size
        dummy_width = 300 if body_shape == "Slim" else 350 if body_shape == "Athletic" else 400
        dummy_height = 500 if size == "S" else 550 if size == "M" else 600 if size == "L" else 650
        dummy_model = dummy_model.resize((dummy_width, dummy_height), Image.Resampling.LANCZOS)

        # Resize user face and t-shirt
        user_face = user_face.resize((100, 100), Image.Resampling.LANCZOS)
        tshirt_img = tshirt_img.resize((dummy_width, dummy_height // 2), Image.Resampling.LANCZOS)

        # Paste images onto dummy model
        dummy_model.paste(user_face, (dummy_width // 2 - 50, 50), user_face)
        dummy_model.paste(tshirt_img, (0, dummy_height // 2), tshirt_img)

        # Save output
        dummy_model.save(output_path, "PNG")
        output_url = url_for("static", filename="uploads/output.png", _external=True)
        logging.info(f"Clothing applied successfully: {output_url}")
        return jsonify({"message": "Success", "output_image": output_url})

    except Exception as e:
        logging.error(f"Error processing images: {str(e)}")
        return jsonify({"error": f"Error processing images: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)