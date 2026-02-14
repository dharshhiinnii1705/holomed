"""
Small Flask app to upload a DICOM file into the project and run the DICOM loader.

Usage:
  1. Install dependencies: `pip install -r requirements.txt`
  2. Run: `python scripts/upload_dicom.py`
  3. Open http://127.0.0.1:5000/ in your browser and upload a .dcm file.
"""
import os
import sys
from pathlib import Path
from flask import Flask, request, render_template_string
from werkzeug.utils import secure_filename

# Ensure project root is on sys.path so `scripts` can be imported when this
# file is executed as a script (python scripts/upload_dicom.py)
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from scripts.dicom_loader import DICOMLoader


BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = BASE_DIR / "data" / "scripts" / "hardware"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"dcm"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

TEMPLATE = """
<!doctype html>
<title>Upload DICOM</title>
<h1>Upload DICOM file (.dcm)</h1>
<form method=post enctype=multipart/form-data>
  <input type=file name=file>
  <input type=submit value=Upload>
 </form>
<p style="color:green">{{ message }}</p>
<h2>Files in upload folder</h2>
<ul>
{% for f in files %}
  <li>{{ f }}</li>
{% else %}
  <li><i>No files</i></li>
{% endfor %}
</ul>
{% if info %}
<h3>First file info</h3>
<pre>{{ info }}</pre>
{% endif %}
"""


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def upload_and_run():
    message = ""
    if request.method == "POST":
        if "file" not in request.files:
            message = "No file part"
        else:
            f = request.files["file"]
            if f.filename == "":
                message = "No selected file"
            elif allowed_file(f.filename):
                filename = secure_filename(f.filename)
                save_path = Path(app.config["UPLOAD_FOLDER"]) / filename
                f.save(str(save_path))
                message = f"Saved {filename}"
            else:
                message = "Only .dcm files allowed"

    loader = DICOMLoader()
    loader.load_folder(app.config["UPLOAD_FOLDER"])
    files = loader.list_files()
    info = loader.get_info(0) if loader.file_count > 0 else None

    return render_template_string(TEMPLATE, files=files, message=message, info=info)


if __name__ == "__main__":
    print(f"Starting upload server, saving to: {app.config['UPLOAD_FOLDER']}")
    app.run(host="127.0.0.1", port=5000, debug=False)
