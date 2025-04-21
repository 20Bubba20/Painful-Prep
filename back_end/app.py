from flask import Flask, request, jsonify
from pathlib import Path
import tempfile

from two_marker_detect import calculate_two_markers

app = Flask(__name__)

@app.route('/detect', methods=['POST'])
def detect_window_dimensions():
    if 'image' not in request.files or 'marker_size' not in request.form:
        return jsonify({"error": "Missing required parameters"}), 400

    image_file = request.files['image']
    marker_size = request.form['marker_size']

    try:
        marker_size = int(marker_size)
    except ValueError:
        return jsonify({"error": "marker_size must be an integer"}), 400

    # Save the uploaded image to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        image_file.save(tmp_file.name)
        image_path = Path(tmp_file.name)

    try:
        width, height = calculate_two_markers(image_path, marker_size)
        return jsonify({
            "width_in": round(width, 2),
            "height_in": round(height, 2)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
