from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import os
import fitz  # PyMuPDF

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["ALLOWED_EXTENSIONS"] = {"pdf"}

# Create the upload folder if it doesn't exist
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])


# Check if file is a PDF
def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


# Try decoding with different encodings
def try_decoding(data):
    encodings = ["utf-8", "iso-8859-2", "windows-1250"]
    for encoding in encodings:
        try:
            return data.decode(encoding), None
        except UnicodeDecodeError:
            continue
    return None, "Unable to decode with common encodings."


# Extract the first HTML attachment and return its content
def extract_html_content(file_path, password=None):
    doc = fitz.open(file_path)
    if doc.is_encrypted:
        if not password or not doc.authenticate(password):
            return None, "Incorrect password!"

    for i, attachment_name in enumerate(doc.embfile_names()):
        attachment_data = doc.embfile_get(i)
        # Try to decode the attachment using common encodings
        content, error = try_decoding(attachment_data)
        if error:
            return None, error
        return content, None

    doc.close()
    return None, "No HTML attachment found!"


# Route for uploading files
@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # Check if the post request has the file part
        if "file" not in request.files:
            return "No file part"

        file = request.files["file"]
        password = request.form.get("password", "")

        # If user does not select a file
        if file.filename == "":
            return "No selected file"

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            # Extract HTML content from the PDF
            html_content, error = extract_html_content(filepath, password)

            # Delete the uploaded PDF immediately
            os.remove(filepath)

            if error:
                return error

            # Show the HTML content
            return render_template("view.html", content=html_content)

    return render_template("upload.html")


# Main function
if __name__ == "__main__":
    app.run(debug=True)
