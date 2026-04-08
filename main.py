import os
from pathlib import Path
import config
from package.common import pdf_process_pipeline
from package.utility import parse_arguments

def main():
    result = parse_arguments()
    name = result.get("name")
    directory = result.get("directory")
    print(f"name {name}; directory {directory}")

    if directory:
       print("Listing directory contents...")
       # Specify the directory path
       pdf_directory = Path(name)
       # Get all .pdf files in the directory
       pdf_files = list(pdf_directory.glob("*.pdf"))
       # Print the names of the PDF files
       for pdf in pdf_files:
            pname = os.path.join(name, pdf.name)
            print(f"pname {pname}; name {name}")
            pdf_process_pipeline(pname)
    elif name:
       print(f"PDF file: {name}")
       pdf_process_pipeline(name)

# Usage
if __name__ == "__main__":
    main()
    
    # pdf_path = "books/1.pdf"  # Replace with your PDF
    # pdf_process_pipeline(pdf_path)

