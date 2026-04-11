
# OCR_PDF
A OCR_PDF in python converts a PDF book into a searchable PDF file.

## 🚀 Features
* It converts one PDF file
```bash
main.py input.pdf
```
* It converts PDF files from a folder.
```bash
main.py input_folder
```

## 🛠 Installation
* Install Tesseract-OCR and set the path as global in your system environment variables
* Install Poppler and set the Library/bin path as global in your system environment variables (for pdf2image, pdftotext)

```bash
# Clone the repository
git clone https://github.com

# Navigate to the directory
cd yourproject

# (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```
