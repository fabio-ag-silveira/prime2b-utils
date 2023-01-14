import os
from argparse import ArgumentParser


class DeleteVirus(object):
    def __init__(self, input_dir: str, delete_virus: bool) -> None:
        self.input_dir = input_dir
        self.delete_virus = delete_virus

    def del_virus(self):
        """
            Encontra e deleta arquivos suspeitos dentro do diretorio 'uploads' e seus subdiretorios.
            Ex: 'filename.ico', 'filename.php' ou arquivos com nome maior que 4 caracteres, que nao sejam 
            o arquivo '.htaccess'.
        """

        files = [
            os.path.join(path, name)
            for path, _, files in os.walk(self.input_dir)
            for name in files
        ]

        for file in files:
            filename = os.path.split(file)[-1]
            extension = filename.split(".")[-1]
            if extension != "htaccess":
                if (
                    extension == "php"
                    or extension == "ico"
                    or extension == "html"
                    or len(extension) > 4
                ):
                    print("Suspicious file: ", file)

                if delete_virus:
                    if (
                        extension == "php"
                        or extension == "ico"
                        or extension == "html"
                        or len(extension) > 4
                    ):
                        os.remove(file)
                        print("Suspicious file deleted: ", filename)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-i", "--input_dir", type=str, help="Diretorio onde se encontra uploads.",
    )
    parser.add_argument(
        "-d", "--delete_virus", action="store_true", help="Deleta arquivos suspeitos."
    )

    args = parser.parse_args()

    input_dir = args.input_dir
    delete_virus = args.delete_virus

    uploads = DeleteVirus(input_dir, delete_virus)
    uploads.del_virus()
