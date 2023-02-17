import os
import shutil

from tqdm import tqdm
from glob import glob
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
        delete_virus: bool,
    ) -> None:
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.zip_uploads = zip_uploads
        self.delete_virus = delete_virus

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

        files = [
            os.path.join(path, name)
            for path, _, files in os.walk(uploads_path)
            for name in files
        ]

        for file in files:
            filename = os.path.split(file)[-1]
            extension = filename.split(".")[-1]
            if extension != "htaccess":
                if extension not in EXTENSIONS or len(extension) > 4:
                    print("Suspicious file: ", file)
                    if delete_virus:
                        os.remove(file)
                        print("Suspicious file deleted: ", filename)
                else:
                    if self.check_file_content(file):
                        print("Suspicious file: ", file)
                        if delete_virus:
                            os.remove(file)
                            print("Suspicious file deleted: ", filename)
            else:
                with open(file, "w") as write_htaccess:
                    write_htaccess.write(HTACCESS)

    def check_file_content(self, file):
        try:
            with open(file) as read_file:
                first_line = read_file.readline()

            first_line_sliced = first_line[:10]

            if (
                "<?php" in first_line_sliced
                or "<script>" in first_line_sliced
                or "<!DOCTYPE" in first_line_sliced
                or "<html" in first_line_sliced
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
        "-d", "--delete_virus", action="store_true", help="Deleta arquivos suspeitos."
    )

    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir
    zip_uploads = args.zip_uploads
    delete_virus = args.delete_virus

    os.makedirs(output_dir, exist_ok=True)

    uploads = Uploads(input_dir, output_dir, zip_uploads, delete_virus)
    uploads.zip_files()
