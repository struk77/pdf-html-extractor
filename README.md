# PDF and HTML Attachment Extractor

This is a Flask application that extracts and handles PDF and HTML attachments from uploaded PDF files. The application can identify and download PDF attachments, as well as decode HTML attachments.

## Features

- Upload PDF files
- Extract and download PDF attachments
- Decode and display HTML attachments
- Automatically delete temporary files after download

## Requirements

- Python 3.x
- Flask
- PyMuPDF (fitz)

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/struk77/pdf-html-extractor.git
    cd pdf-html-extractor
    ```

2. Create a virtual environment and activate it:

    ```sh
    python3.12 -m venv venv
    source venv/bin/activate
    ```

3. Install the required packages:

    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Run the Flask application:

    ```sh
    python app.py
    ```

2. Open your web browser and go to `http://127.0.0.1:5000`.

3. Upload a PDF file using the provided form.

4. The application will extract and handle the attachments:
    - If the attachment is a PDF, it will be available for download.
    - If the attachment is HTML, it will be displayed.

## Deployment to Heroku

1. Install the Heroku CLI:

    ```sh
    brew tap heroku/brew && brew install heroku
    ```

2. Log in to your Heroku account:

    ```sh
    heroku login
    ```

3. Create a new Heroku application:

    ```sh
    heroku create your-app-name
    ```

4. Add a `Procfile` to the root directory of your project with the following content:

    ```plaintext
    web: python app.py
    ```

5. Commit your changes:

    ```sh
    git add Procfile
    git commit -m "Add Procfile for Heroku deployment"
    ```

6. Push your code to Heroku:

    ```sh
    git push heroku main
    ```

7. Scale the web dyno:

    ```sh
    heroku ps:scale web=1
    ```

8. Open your Heroku application in the browser:

    ```sh
    heroku open
    ```

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.
