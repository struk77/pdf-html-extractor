import tempfile
from flask import Flask, request, render_template, send_file, after_this_request
from werkzeug.utils import secure_filename
import os
import fitz  # PyMuPDF

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["DOWNLOAD_FOLDER"] = "downloads"
app.config["ALLOWED_EXTENSIONS"] = {"pdf"}

# Create the upload folder if it doesn't exist
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

# Create the download folder if it doesn't exist
if not os.path.exists(app.config["DOWNLOAD_FOLDER"]):
    os.makedirs(app.config["DOWNLOAD_FOLDER"])


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


# Extract all HTML and PDF attachments
def extract_content(file_path, password=None):
    doc = fitz.open(file_path)
    if doc.is_encrypted:
        if not password or not doc.authenticate(password):
            return None, "Incorrect password!"

    attachments = []
    for i, attachment_name in enumerate(doc.embfile_names()):
        attachment_data = doc.embfile_get(i)

        if attachment_data[:4] == b"%PDF":
            # Save the PDF attachment to a temporary file in downloads folder
            temp_file_path = os.path.join(
                app.config["DOWNLOAD_FOLDER"], f"attachment_{i}.pdf"
            )
            with open(temp_file_path, "wb") as f:
                f.write(attachment_data)
            attachments.append((temp_file_path, "pdf", None))

        else:
            # Try to decode the attachment using common encodings
            content, error = try_decoding(attachment_data)
            if error:
                attachments.append((None, None, error))
            else:
                attachments.append((content, "html", None))

    doc.close()

    if attachments:
        return attachments
    else:
        return None, "No HTML or PDF attachments found!"


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

            # Extract attachments using the provided password
            attachments = extract_content(filepath, password)

            if not attachments:
                return "No attachments found or incorrect password"

            # Display all attachments
            response = ""
            for attachment in attachments:
                if attachment[1] == "pdf":
                    response += f'<a href="/download/{os.path.basename(attachment[0])}">Download PDF Attachment {os.path.basename(attachment[0])}</a><br>'
                elif attachment[1] == "html":
                    response += f"HTML Attachment content:<br>{attachment[0]}<br>"
                else:
                    response += f"Error: {attachment[2]}<br>"

            # Delete the uploaded PDF immediately
            os.remove(filepath)

            return response

    return render_template("upload.html")


@app.route("/download/<filename>")
def download_file(filename):
    filepath = os.path.join(app.config["DOWNLOAD_FOLDER"], filename)
    if os.path.exists(filepath):

        @after_this_request
        def delete_file(response):
            try:
                os.remove(filepath)  # Delete the file after sending
            except Exception as e:
                print(f"Error while deleting file: {e}")
            return response

        return send_file(filepath, as_attachment=True)
    else:
        return "File not found", 404


# Main function
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG") == "TRUE"
    app.run(host="127.0.0.1", port=port, debug=debug)
