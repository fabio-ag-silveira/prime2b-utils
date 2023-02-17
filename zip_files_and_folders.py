import os
import shutil
import zipfile

from tqdm import tqdm
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
        self.directories_list = set(os.scandir(self.input_dir))

    def zip_files(self) -> None:
        """
        Compress files/directories that are inside the input directory and save them in the specified directory.
        """

        for entry in tqdm(self.directories_list):

            output_filename = entry.name.replace(".", "_")
            zip_file_path = os.path.join(self.output_dir, output_filename)

            print("\nFilename: ", entry.path, "\n")

            if entry.is_dir():
                shutil.make_archive(zip_file_path, "zip", entry.path)
                print("\nZip created: ", zip_file_path, "\n")
            else:
                if entry.is_file():
                    with zipfile.ZipFile(
                        zip_file_path + ".zip", "w", compression=zipfile.ZIP_DEFLATED
                    ) as zip_file:
                        # add the file to the zip file
                        zip_file.write(entry.path, entry.name)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_dir",
        type=str,
        help="Directory where all the files/directories to be compressed are located.",
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        type=str,
        default=".{}zip".format(sp),
        help="Directory where the .zip files of the input folder will be saved.",
    )

    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir

    os.makedirs(output_dir, exist_ok=True)

    zip = Zip(input_dir, output_dir)
    zip.zip_files()
