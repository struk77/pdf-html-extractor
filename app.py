import tempfile
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


# Function to handle the download and deletion of the PDF file
def download_and_delete_pdf(file_path):
    with open(file_path, "rb") as f:
        pdf_data = f.read()
    os.remove(file_path)
    return pdf_data


# Extract the first HTML attachment and return its content
def extract_html_content(file_path, password=None):
    doc = fitz.open(file_path)
    if doc.is_encrypted:
        if not password or not doc.authenticate(password):
            return None, "Incorrect password!"

    for i, attachment_name in enumerate(doc.embfile_names()):
        attachment_data = doc.embfile_get(i)

        if attachment_data[:4] == b"%PDF":
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            temp_file.write(attachment_data)
            temp_file.close()
            return temp_file.name, None

        # Try to decode the attachment using common encodings
        content, error = try_decoding(attachment_data)
        if error:
            return None, error
        return content, None

    doc.close()
    return None, "No HTML or PDF attachment found!"


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

            if html_content.endswith(".pdf"):
                pdf_data = download_and_delete_pdf(html_content)
                return pdf_data

            # Delete the uploaded PDF immediately
            os.remove(filepath)

            if error:
                return error

            # Show the HTML content
            return render_template("view.html", content=html_content)

    return render_template("upload.html")


# Main function
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
