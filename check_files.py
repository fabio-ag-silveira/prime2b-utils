import os

from PIL import Image
from argparse import ArgumentParser

sp = os.path.sep

HTACCESS = """
<FilesMatch ".(py|exe|php)$">
 Order allow,deny
 Deny from all
</FilesMatch>

<FilesMatch "^(about.php|radio.php|index.php|content.php|lock360.php|admin.php|wp-login.php)$">
 Order allow,deny
 Deny from all
</FilesMatch>
"""

EXTENSIONS = {
    "bmp",
    "jpg",
    "xml",
    "gif",
    "jpeg",
    "pdf",
    "webp",
    "tiff",
    "svg",
    "mp4",
    "json",
    "png",
    "avi",
    "mkv",
    "mov",
}


class SuspiciousFileChecker(object):
    def __init__(self, input_dir: str, delete_suspicious_file: bool) -> None:
        self.input_dir = input_dir
        self.delete_suspicious_file = delete_suspicious_file

        self.all_file_paths = [
            os.path.join(root, filename)
            for root, _, files in os.walk(input_dir)
            for filename in files
        ]

    def find_suspicious_files(self) -> None:
        """
        Find suspicious files on the specified directory and its subdirectories.
        The '.htaccess' file will be rewritten with new rules.
        """
        number_of_suspicious_files = 0

        for file_path in self.all_file_paths:
            filename = os.path.basename(file_path)
            if filename.endswith(".htaccess"):
                with open(file_path, "w") as write_htaccess:
                    write_htaccess.write(HTACCESS)
            else:
                extension = os.path.splitext(filename)[1].lower()[1:]
                if extension not in EXTENSIONS or len(extension) > 4:
                    number_of_suspicious_files += 1
                    print("Suspicious file: ", file_path)
                    self.delete_file(file_path)
                else:
                    if self.check_file_content(file_path):
                        number_of_suspicious_files += 1
                        print("Suspicious file: ", file_path)
                        self.delete_file(file_path)

        print("\n{} suspicious files were found.\n".format(number_of_suspicious_files))

        if self.delete_suspicious_file and number_of_suspicious_files > 0:
            print(
                "All {} suspicious files was deleted.\n".format(
                    number_of_suspicious_files
                )
            )
            number_of_suspicious_files = 0

    def delete_file(self, file_path) -> None:
        """
        Delete the suspicious file.
        """
        if self.delete_suspicious_file:
            os.remove(file_path)

    def check_file_content(self, file):
        """
        Check the file contents. Returns True if the file has HTML or image/video content,
        otherwise returns False.
        """
        html_php_tags = ["<?php", "<!doctype", "<html", "<head", "<body", "<script"]

        # Check for image or video content
        try:
            img = Image.open(file)
            img_format = img.format
            if img_format in [
                "JPEG",
                "PNG",
                "GIF",
                "BMP",
                "TIFF",
                "WEBP",
                "AVI",
                "MP4",
                "MKV",
                "MOV",
            ]:
                return False
        except:
            with open(file, "rb") as f:
                header = f.read(32)

            first_line = header.decode("utf-8")

            # Check for HTML or PHP content
            if any(
                html_php_tag in first_line.lower() for html_php_tag in html_php_tags
            ):
                return True
            else:
                return False


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_dir",
        type=str,
        help="Path to the specified directory.",
    )
    parser.add_argument(
        "-d",
        "--delete_suspicious_file",
        action="store_true",
        help="Delete the suspicious files.",
    )

    args = parser.parse_args()

    input_dir = args.input_dir
    delete_suspicious_file = args.delete_suspicious_file

    uploads = SuspiciousFileChecker(input_dir, delete_suspicious_file)
    uploads.find_suspicious_files()
