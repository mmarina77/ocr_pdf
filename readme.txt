
# Create the environment



install Tesseract-OCR and set the path as global in your system environment variables

# for pdf2image, pdftotext
Install Poppler and set the Library/bin path as global in your system environment variables


# Windows
python -m venv .venv

# macOS/Linux
python3 -m venv .venv

# Activate it:

# Windows: 
	.venv\Scripts\activate
# macOS/Linux: 
	source .venv/bin/activate

pip install uv  # Install uv globally if you haven't
mkdir my_project && cd my_project
uv init         # Generates pyproject.toml, README.md, and .gitignore


poetry new my_project  # Creates a full project structure
# OR in an existing folder:
poetry init           # Interactive wizard to create pyproject.toml


# Install from File
pip install -r requirements.txt
