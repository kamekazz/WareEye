import cv2
import numpy as np
from flask import Flask, request, render_template_string, send_file
from io import BytesIO

app = Flask(__name__)

INDEX_HTML = '''
<!doctype html>
<title>OpenCV Flask App</title>
<h1>Upload an image to convert to grayscale</h1>
<form method=post enctype=multipart/form-data action="/process">
  <input type=file name=file>
  <input type=submit value=Upload>
</form>
'''

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/process', methods=['POST'])
def process():
    file = request.files.get('file')
    if not file:
        return "No file uploaded", 400

    file_bytes = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if img is None:
        return "Invalid image", 400

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, buf = cv2.imencode('.png', gray)
    return send_file(BytesIO(buf.tobytes()), mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
