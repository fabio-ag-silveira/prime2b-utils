import os
import shutil

from tqdm import tqdm
from glob import glob
from argparse import ArgumentParser
from PIL import Image

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

EXTENSIONS = [
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


class Uploads(object):
    def __init__(
        self,
        input_dir: str,
        output_dir: str,
        zip_uploads: bool,
        delete_suspicious_file: bool,
    ) -> None:
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.zip_uploads = zip_uploads
        self.delete_suspicious_file = delete_suspicious_file

        self.directories_com = list(glob(os.path.join(self.input_dir, "*.com")))
        self.directories_br = list(glob(os.path.join(self.input_dir, "*.br")))

        self.directories_list = set(self.directories_com + self.directories_br)

    def zip_files(self) -> None:
        """
        Compacta o diretorio de uploads de cada site e salva no diretorio especificado.
        """

        for path in tqdm(self.directories_list):

            uploads_dir = "htdocs{}wp-content{}uploads".format(sp, sp)
            uploads_path = os.path.join(path, uploads_dir)
            output_filename = os.path.split(path)[-1].replace(".", "_")
            zip_file_path = os.path.join(self.output_dir, output_filename)

            print("\nFilename: ", path, "\n")

            self.del_virus(uploads_path)

            if self.zip_uploads:
                try:
                    shutil.make_archive(zip_file_path, "zip", uploads_path)
                    print("\nZip created: ", zip_file_path, "\n")
                except FileNotFoundError:
                    print("Diretorio de uploads nao encontrado.")

    def del_virus(self, uploads_path) -> None:
        """
        Encontra e deleta arquivos suspeitos dentro do diretorio 'uploads' e seus subdiretorios.
        Ex: 'filename.ico', 'filename.php' ou arquivos com nome maior que 4 caracteres, que nao sejam
        o arquivo '.htaccess'. Arquivos '.htaccess' sao reescritos com as permissoes alteradas.
        """
        number_of_suspicious_files = 0

        files = [
            os.path.join(path, name)
            for path, _, files in os.walk(uploads_path)
            for name in files
        ]

        for file_path in files:
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
        help="Diretorio onde se encontra todos os sites (geralmente a pasta 'www' do servidor).",
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        type=str,
        default=".{}uploads_zip".format(sp),
        help="Diretorio onde os arquivos .zip da pasta 'uploads' serao salvos.",
    )
    parser.add_argument(
        "-z", "--zip_uploads", action="store_true", help="Compacta a pasta 'uploads'."
    )
    parser.add_argument(
        "-d",
        "--delete_suspicious_file",
        action="store_true",
        help="Deleta arquivos suspeitos.",
    )

    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir
    zip_uploads = args.zip_uploads
    delete_suspicious_file = args.delete_suspicious_file

    os.makedirs(output_dir, exist_ok=True)

    uploads = Uploads(input_dir, output_dir, zip_uploads, delete_suspicious_file)
    uploads.zip_files()
