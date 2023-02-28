import os
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

ALLOWED_EXTENSIONS = [
    "bmp",
    "jpg",
    "xml",
    "gif",
    # "js",
    "jpeg",
    # "css",
    "pdf",
    "webp",
    "tiff",
    "svg",
    "mp4",
    "json",
    "png",
]

# ALL_EXTENSIONS = []


class FilesAnalyzer(object):
    def __init__(self, input_dir: str, delete_suspicious_file: bool) -> None:
        self.input_dir = input_dir
        self.delete_suspicious_file = delete_suspicious_file

    def analyze_files(self) -> None:
        """
        Find and delete suspicious files on the specified directory and its subdirectories.
        The '.htaccess' file will be rewritten with new rules.
        """
        number_of_suspicious_files = 0

        if self.input_dir.endswith(sp):
            root_folder_name = os.path.split(self.input_dir)[-2]
        else:
            root_folder_name = os.path.split(self.input_dir + sp)[-2]

        files = [
            os.path.join(path, name)
            for path, _, files in os.walk(self.input_dir)
            for name in files
        ]

        for file in files:
            filename = os.path.split(file)[-1]
            extension = filename.split(".")[-1].lower()
            root_to_file_path = file.split(root_folder_name)[-1]
            # ALL_EXTENSIONS.append(extension)
            if extension != "htaccess":
                if extension not in ALLOWED_EXTENSIONS or len(extension) > 4:
                    number_of_suspicious_files += 1
                    print("Suspicious file: ", root_to_file_path)
                    if delete_suspicious_file:
                        os.remove(file)
                else:
                    if self.check_file_content(file):
                        number_of_suspicious_files += 1
                        print("Suspicious file: ", root_to_file_path)
                        if delete_suspicious_file:
                            os.remove(file)
            else:
                with open(file, "w") as write_htaccess:
                    write_htaccess.write(HTACCESS)
        # print(set(ALL_EXTENSIONS))

        print("\n{} suspicious files were found.\n".format(number_of_suspicious_files))

        if self.delete_suspicious_file and number_of_suspicious_files > 0:
            print(
                "All {} suspicious files have been deleted.\n".format(
                    number_of_suspicious_files
                )
            )
            number_of_suspicious_files = 0

    def check_file_content(self, file):
        """
        Check the file contents. Returns True if the file has HTML or PHP content,
        otherwise returns False.
        """
        html_php_tags = ["<?php", "<!doctype", "<html", "<head", "<body", "<script"]

        try:
            with open(file) as read_file:
                first_line = read_file.readline()

            first_line_sliced = first_line[:10]

            if any(
                html_php_tag in first_line_sliced.lower()
                for html_php_tag in html_php_tags
            ):
                return True
            else:
                return False
        except:
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

    file_analyzer = FilesAnalyzer(input_dir, delete_suspicious_file)
    file_analyzer.analyze_files()
