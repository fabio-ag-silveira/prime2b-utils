import os
import shutil

from tqdm import tqdm
from glob import glob
from argparse import ArgumentParser

sp = os.path.sep


class Uploads(object):
    def __init__(self, input_dir: str, output_dir: str) -> None:
        self.input_dir = input_dir
        self.output_dir = output_dir

        self.directories_com = list(glob(os.path.join(self.input_dir, "*.com")))
        self.directories_com_br = list(glob(os.path.join(self.input_dir, "*.com.br")))
        self.directories_list = set(self.directories_com + self.directories_com_br)

    def zip_files(self):

        for path in tqdm(self.directories_list):

            uploads_dir = f"htdocs{sp}wp-content{sp}uploads"
            uploads_path = os.path.join(path, uploads_dir)
            output_filename = os.path.split(path)[-1].replace(".", "_")
            zip_file_path = os.path.join(self.output_dir, output_filename)

            print("\nZip filename: ", output_filename, "\n")

            shutil.make_archive(zip_file_path, "zip", uploads_path)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_dir",
        type=str,
        default=f".{sp}gowebbyhf38{sp}gowebbyhf38{sp}www",
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        type=str,
        default=f".{sp}gowebbyhf38{sp}gowebbyhf38{sp}gowebbyhf38_uploads_zip",
    )

    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir

    os.makedirs(output_dir, exist_ok=True)

    uploads = Uploads(input_dir, output_dir)
    uploads.zip_files()
