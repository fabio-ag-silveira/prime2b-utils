import os

from subprocess import run
from glob import glob
from argparse import ArgumentParser

sp = os.path.sep


HTACCESS_UPLOADS_RULES = """
<FilesMatch ".(py|exe|php)$">
 Order allow,deny
 Deny from all
</FilesMatch>

<FilesMatch "^(about.php|radio.php|index.php|content.php|lock360.php|admin.php|wp-login.php)$">
 Order allow,deny
 Deny from all
</FilesMatch>
"""

HTACCESS_ROOT_RULES = """
<Files wp-config.php>
order allow,deny
deny from all
</Files>

<files .htaccess>
order allow,deny
deny from all
</files>

# Block the include-only files.
RewriteEngine On
RewriteBase /
RewriteRule ^wp-admin/includes/ - [F,L]
RewriteRule !^wp-includes/ - [S=3]
RewriteRule ^wp-includes/[^/]+\.php$ - [F,L]
RewriteRule ^wp-includes/js/tinymce/langs/.+\.php - [F,L]
RewriteRule ^wp-includes/theme-compat/ - [F,L]
# BEGIN WordPress

<FilesMatch "\.(jpg|jpeg|jpe|gif|png|bmp|tif|tiff)$">
Order Deny,Allow
Allow from all
</FilesMatch>

<FilesMatch "\.(php|php\.)(.+)(\w|\d)$">
Order Allow,Deny
Deny from all
</FilesMatch>

# Desabilitar listagem de diretorios
Options -Indexes
"""

ALLOWED_EXTENSIONS = [
    "woff",
    "bmp",
    "jpg",
    "xml",
    "gif",
    "js",
    "jpeg",
    "css",
    "pdf",
    "webp",
    "tiff",
    "svg",
    "mp4",
    "json",
    "png",
    "xlsx",
]


class CheckFiles(object):
    def __init__(
        self,
        input_dir: str,
        delete_suspicious_file: bool,
    ) -> None:
        self.input_dir = input_dir
        self.delete_suspicious_file = delete_suspicious_file

        self.directories_and_files_list = list(glob(os.path.join(self.input_dir, "*")))
        self.files_list = list(glob(os.path.join(self.input_dir, "*.*")))

    def analyzer(self) -> None:

        cmd = ["wp", "option", "get", "siteurl"]

        for path in self.directories_and_files_list:

            if path not in self.files_list:

                print("\nFilename: ", path)

                public_html_path = os.path.join(path, "public_html")
                htaccess_root_path = os.path.join(path, "public_html", ".htaccess")
                uploads_path = os.path.join(
                    path, "public_html", "wp-content", "uploads"
                )

                public_html_files = list(glob(os.path.join(public_html_path, "*")))
                print("Number of files in public_html: ", len(public_html_files), "\n")

                if os.path.isfile(htaccess_root_path):
                    self.add_rules_htaccess_root(htaccess_root_path)

                # site_url = run(cmd, capture_output=True, cwd=public_html_path).stdout

                # print("Site URL: ", site_url)

                # if len(site_url) > 4:

                #     output_filename = (
                #         str(site_url).replace(".", "_").split("\\")[-2].split("/")[-1]
                #     )

                #     print("output: ", output_filename, "\n")

                # if len(public_html_files) > 2:
                #     self.analyze_files(uploads_path)

    def add_rules_htaccess_root(self, htaccess_path):
        """
        Add rules to the .htaccess file of the root directory.
        """

        with open(htaccess_path, encoding="utf-8", errors="ignore") as htaccess_root:
            data = htaccess_root.read()

            if """<FilesMatch "\.(jpg|jpeg|jpe|gif|png|bmp|tif|tiff)$">""" not in data:

                # Open the file in append & read mode ('a+')
                with open(
                    htaccess_path, "a+", encoding="utf-8", errors="ignore"
                ) as file_object:
                    # Move read cursor to the start of file.
                    file_object.seek(0)
                    # If file is not empty then append '\n'
                    data = file_object.read(100)
                    if len(data) > 0:
                        file_object.write("\n")
                    # Append text at the end of file
                    file_object.write(HTACCESS_ROOT_RULES)

    def analyze_files(self, uploads_path: str) -> None:
        """
        Find and delete suspicious files on the specified directory and its subdirectories.
        The '.htaccess' file will be rewritten with new rules.
        """
        number_of_suspicious_files = 0

        if uploads_path.endswith(sp):
            root_folder_name = os.path.split(uploads_path)[-2]
        else:
            root_folder_name = os.path.split(uploads_path + sp)[-2]

        files = [
            os.path.join(path, name)
            for path, _, files in os.walk(uploads_path)
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
                    if self.delete_suspicious_file:
                        os.remove(file)
                else:
                    if self.check_file_content(file):
                        number_of_suspicious_files += 1
                        print("Suspicious file: ", root_to_file_path)
                        if self.delete_suspicious_file:
                            os.remove(file)
            else:
                with open(file, "w") as write_htaccess:
                    write_htaccess.write(HTACCESS_UPLOADS_RULES)
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
        help="Diretorio onde se encontra todos os sites (geralmente a pasta 'www' do servidor).",
    )
    parser.add_argument(
        "-d",
        "--delete_suspicious_file",
        action="store_true",
        help="Deleta arquivos suspeitos.",
    )

    args = parser.parse_args()

    input_dir = args.input_dir
    delete_suspicious_file = args.delete_suspicious_file

    check_files = CheckFiles(input_dir, delete_suspicious_file)
    check_files.analyzer()
