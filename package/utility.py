import os
from pathlib import Path
import argparse

def make_dir(path):
    os.makedirs(path, exist_ok=True)
    # if not os.path.exists(path):
    #     os.makedirs(path)

def path_info(path):
    base_name = Path(path).stem
    root = Path(path).parent
    extension = Path(path).suffix
    ext = extension[1:] if extension.startswith('.') else extension
    filename = Path(path).name
    return {
        "file_path": root,
        "base_name": base_name,
        "extension": extension,
        "filename": filename,
        "ext": ext
    }

def parse_arguments():
    # 1. Initialize the parser
    parser = argparse.ArgumentParser(description="Parse command line arguments.")

    # 2. Add arguments
    # Positional argument (required)
    parser.add_argument("name", help="The file or directory path.")

    # Boolean flag (True if present, False if absent)
    # parser.add_argument("-d", "--directory", default=False, help="The directory.")

    # 3. Parse the arguments
    args = parser.parse_args()

    name_arg = path_info(args.name)
    print(f"args: {args}")
    # mime_type = mimetypes.guess_type(args.name)[0] 
    # print(f"mime_type: {mime_type}")

    path = Path(args.name)

    if path.is_file() and name_arg.get("ext").lower() == "pdf":
        print("This path points to a file.")
        return {"name": args.name, "directory": False}
    elif path.is_dir():
        print("This path points to a directory.")
        return {"name": args.name, "directory": True}
    elif not path.exists():
        print("The specified path does not exist.")
        return {"name": None, "directory": None}


