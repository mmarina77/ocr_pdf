import config
import pymupdf as fitz
import os
import cv2 as cv
import pytesseract

import ocrmypdf
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter

# hye-calfa-n

def extract_images(pdf_path, output_dir):
    """Extract embedded images to books_images/"""
    
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
	
    #print(f"doc: {doc}")
    processed_images = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        #print(f"page: {page}")
        image_list = page.get_images(full=True)
        for img_idx, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            #image_name = os.path.join(output_dir, f"page_{page_num+1:03d}.png")
            image_name = f"{output_dir}/page{page_num:02d}_img{img_idx:02d}.{image_ext}"
            with open(image_name, "wb") as f:
                f.write(image_bytes)
                processed_images.append(image_name)
            #print(f"Extracted: {image_name}")
    doc.close()
    return processed_images


def filter_image_cleaning(image_path):           # remove_noise
    # Load image using OpenCV
    img = cv.imread(image_path)
    
    # 1. Convert to grayscale
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    
    # 2. Apply Median Blur to remove noise while keeping edges sharp
    # Use an odd number like 3 or 5. 3 is usually enough for most scans.
    blurred = cv.medianBlur(gray, 3)
    
    # 2. Apply thresholding (Otsu's Binarization)
    # This automatically finds the best threshold value
    _, thresh = cv.threshold(blurred, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    
    # 3. Optional: Resize if text is too small
    #thresh = cv.resize(thresh, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    return thresh


def run_filter(images, out_images_dir):
    """ 2. Run Filtering (Denoising) on the image """
    for image_path in images:
        
        clean_img = filter_image_cleaning(image_path)
        
        # Save the cleaned image to the output directory
        output_path = os.path.join(out_images_dir, os.path.basename(image_path))
        
        #print(f"output_path - {output_path} - {clean_img.shape}")
        cv.imwrite(output_path, clean_img)


###############################

def extract_text_from_image(image_path):
    
    # Load the image
    img = cv.imread(image_path)

    # Preprocess the image
    # processed_img = preprocess_image(img)

    # Extract text using Tesseract
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(img, lang=config.OCR_LANG, config=custom_config) # 'hye+ru'

    return text

def save_text(images_dir, text_file):

    ext_txt = open(text_file, 'a', encoding='utf-8')
    for filename in os.listdir(images_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff')):
            img_path = os.path.join(images_dir, filename)
            
            text = extract_text_from_image(img_path)
            ext_txt.write(f"\n--- {filename} ---\n")
            ext_txt.write(text.strip())
            ext_txt.write("\n" + "="*30 + "\n")

################################
def directory_files(path):
    """Returns a list of paths to files in a directory."""
    contents = os.listdir(path)
    files = []
    for item in contents:
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path):
            files.append(item_path)
    return files

def assemble_pdf(books_images_dir, output_pdf):
    """Assemble images from books_images/ into PDF in same folder"""
    image_files = directory_files(books_images_dir)
    
    if not image_files:
        print("No images found in books_images/")
        return
    
    images = []

    for img_path in image_files:
        img = Image.open(img_path).convert("RGB")
        images.append(img)
    
    #output_pdf = "books_images/assembled.pdf"
    images[0].save(
        output_pdf,
        "PDF", 
        resolution=150.0,
        save_all=True,
        append_images=images[1:]
    )
    print(f"Assembled PDF: {output_pdf}")
    
    
def update_pdf_images(pdf_path, folder_path, output_path):
    '''Update images in a PDF with new images from a folder.'''
    doc = fitz.open(pdf_path)
    
    # Get sorted images from your folder
    new_images = sorted([
        os.path.join(folder_path, f) for f in os.listdir(folder_path) 
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ])
    
    img_idx = 0
    for page in doc:
        # Get all images on the current page
        image_info_list = page.get_images(full=True)
        
        for img_info in image_info_list:
            if img_idx < len(new_images):
                xref = img_info[0]  # The first element is the XREF ID
                new_img_path = new_images[img_idx]
                
                # CORRECT CALL: page.replace_image(xref, filename=...)
                # This replaces the pixels and updates the metadata (width/height)
                page.replace_image(xref, filename=new_img_path)
                
                # print(f"Replaced XREF {xref} on page {page.number} with {new_img_path}")
                img_idx += 1
            else:
                break

    # IMPORTANT: 'garbage=4' deletes the old image data permanently
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    
    
def image_enhance(image_path):
    """Process the image for OCR."""
    img = Image.open(image_path).convert("RGB")

    # Adjust contrast - Enhance image quality
    #enhancer = ImageEnhance.Contrast(img)
    #img = enhancer.enhance(2.0)

    # Adjust brightness
    brightness_converter = ImageEnhance.Brightness(img)
    img = brightness_converter.enhance(1.5)     #1.2

    # Apply a blur filter
    #blurred_img = img.filter(ImageFilter.BLUR)
    
    img.save(image_path)

def convert_scanned_pdf(input_file_path, output_file_path):
    """Converts a scanned PDF into a searchable PDF using ocrmypdf."""
    try:
        # The ocr() function takes input and output file paths as arguments
        ocrmypdf.ocr(
            input_file_path, 
            output_file_path,
            deskew=True,        # Corrects crooked pages
            rotate_pages=True,      # Automatically rotates misaligned pages
            #oversample=300,         # Resample images to 300 DPI
            language=config.OCR_LANG,   # Supports multiple languages
            skip_text=True
        )
        print(f"File converted successfully and saved to: {output_file_path}")
    except ocrmypdf.exceptions.PriorOcrFoundError:
        print("Note: The input PDF already had text. Use force_ocr=True to re-process.")
        #pass
    except Exception as e:
        print(f"An error occurred: {e}")
        #pass
                
# OCR process for a PDF file
def process_pdf_for_ocr(original_pdf_path, work_dir):
    """Complete OCR pipeline."""
    print(f"Processing PDF: {original_pdf_path} in work directory: {work_dir}")

    # Files paths
    base_name = Path(original_pdf_path).stem
    tmp_pdf = os.path.join(work_dir, config.WORK_OCR_DIR, f"{base_name}_tmp.pdf")
    grey_tmp_pdf = os.path.join(work_dir, config.WORK_OCR_DIR, f"{base_name}_grey_tmp.pdf")
    tmp_txt = os.path.join(work_dir, f"{base_name}_text.txt")
    orig_searchable_pdf = os.path.join(work_dir, f"{base_name}_searchable.pdf")

    orig_images_dir = os.path.join(work_dir, config.WORK_IMAGES_DIR)
    filtered_images_dir = os.path.join(work_dir, config.WORK_FILTERED_IMAGES_DIR)

    # 1. Split and process images
    print("1. Splitting PDF to images...")
    images_list = extract_images(original_pdf_path, orig_images_dir)
    print(f"Extracted {len(images_list)} images.")
    
    # 2. Image filtering process
    print("2. Image filtering process...")
    run_filter(images_list, filtered_images_dir)

    # 3. Extract OCR text to file
    print("3. Extracting OCR text to file...")
    # to_json(filtered_images_dir, tmp_txt, raw_json_dir, coords_json_dir)
    save_text(filtered_images_dir, tmp_txt)

    # 4. Reassemble PDF from processed images
    print("4. Reassembling PDF from processed images...")
    assemble_pdf(filtered_images_dir, tmp_pdf)

    # 5. OCR with ocrmypdf
    print("5. Running OCR with ocrmypdf...")
    convert_scanned_pdf(tmp_pdf, grey_tmp_pdf)
    
    # 6. Update original PDF with new images
    print("6. Updating original PDF with new images...")
    update_pdf_images(grey_tmp_pdf, orig_images_dir, orig_searchable_pdf)

# Helper function to initialize directories for a given PDF
def initialize_directories(work, original_pdf_path, dirs):
    base_name = Path(original_pdf_path).stem
    book_work_dir = os.path.join(work, base_name)
    for dir in dirs:
        new_dir = os.path.join(book_work_dir, dir)
        os.makedirs(new_dir, exist_ok=True)
    return book_work_dir


def pdf_process_pipeline(pdf_path):
    """Complete OCR pipeline."""
    
    work_dir = initialize_directories(config.WORK_DIR, pdf_path, [
        config.WORK_IMAGES_DIR,
        config.WORK_OCR_DIR,
        config.WORK_FILTERED_IMAGES_DIR
    ])
    process_pdf_for_ocr(pdf_path, work_dir)
    