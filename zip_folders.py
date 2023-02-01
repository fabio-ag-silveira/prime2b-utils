import os
import shutil

from tqdm import tqdm
from glob import glob
from argparse import ArgumentParser

sp = os.path.sep


class Zip(object):
    def __init__(
        self,
        input_dir: str,
        output_dir: str,
    ) -> None:
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.directories_list = set(list(glob(os.path.join(self.input_dir, "*"))))

    def zip_files(self) -> None:
        """
        Compacta arquivos/diretorios que estao dentro de diretorio de input e salva no 
        diretorio especificado.
        """

        for path in tqdm(self.directories_list):

            output_filename = os.path.split(path)[-1].replace(".", "_")
            zip_file_path = os.path.join(self.output_dir, output_filename)

            print("\nFilename: ", path, "\n")

            try:
                shutil.make_archive(zip_file_path, "zip", path)
                print("\nZip created: ", zip_file_path, "\n")
            except FileNotFoundError:
                print("Diretorio nao encontrado.")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_dir",
        type=str,
        help="Diretorio onde se encontra todos os arquivos/diretorios que serao compactados.",
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        type=str,
        default=".{}zip".format(sp),
        help="Diretorio onde os arquivos .zip da pasta de input serao salvos.",
    )

    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir

    os.makedirs(output_dir, exist_ok=True)

    zip = Zip(input_dir, output_dir)
    zip.zip_files()
