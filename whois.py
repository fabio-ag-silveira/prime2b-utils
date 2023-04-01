import requests
import time
import pandas as pd

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class Whois(object):
    def __init__(self, csv_path, output_csv_path, session):
        self.csv_path = csv_path
        self.output_csv_path = output_csv_path
        self.session = session

    def verifica_dominios(self):

        df = pd.read_csv(self.csv_path)
        colunas = [
            "Titular",
            "Contato Tecnico",
            "Servidor DNS",
            "Status do dominio",
            "Observacao",
        ]

        for coluna in colunas:
            if coluna not in df.columns:
                df[coluna] = ""

        for index, row in df.iterrows():

            domain = row["Dominio"]
            print(f"Dominio: {domain}")
            time.sleep(3)

            if domain.endswith("br"):
                self.registro_br_api(domain, df, index)
            else:
                self.whois_api_ninja(domain, df, index)

            df.to_csv(self.output_csv_path, index=False)

        df.fillna("-", inplace=True)
        df.to_csv(self.output_csv_path, index=False)

    def registro_br_api(self, domain, df, index):

        url = f"https://rdap.registro.br/domain/{domain}"
        # A GET request to the API
        response = self.session.get(url)

        if response.status_code == 200:
            response_json = response.json()
            try:
                # dominio = response_json["ldhName"]
                titular = response_json["entities"][0]["legalRepresentative"]
                contato = response_json["entities"][1]["handle"]
                status = response_json["status"][0]
                nameserver = response_json["nameservers"][0]["ldhName"]

                df.at[index, "Titular"] = titular
                df.at[index, "Contato Tecnico"] = contato
                df.at[index, "Servidor DNS"] = nameserver
                df.at[index, "Status do dominio"] = status

            except Exception:
                observacao = "Dominio indisponivel"
                print(observacao)
                df.at[index, "Observacao"] = observacao

        elif response.status_code == 404:
            observacao = "Recurso inexistente"
            print(observacao)
            df.at[index, "Observacao"] = observacao
        else:
            print(domain, " Problema na requisicao: ", response.status_code)

    def whois_api_ninja(
        self, domain, df, index, api_key="RmiB1MRy21QLOa62PBmuzw==yOWXWsVlftnqJFBE"
    ):

        api_url = f"https://api.api-ninjas.com/v1/whois?domain={domain}"
        response = session.get(api_url, headers={"X-Api-Key": api_key})

        if response.status_code == 200:
            # Print the response
            response_json = response.json()
            try:
                # dominio = response_json["domain_name"]
                titular = response_json["name"]
                nameserver = response_json["name_servers"][0]

                df.at[index, "Titular"] = titular
                df.at[index, "Servidor DNS"] = nameserver

            except Exception:
                observacao = "Dominio indisponivel"
                df.at[index, "Observacao"] = observacao
        elif response.status_code == 404:
            observacao = "Recurso inexistente"
            df.at[index, "Observacao"] = observacao
        else:
            print("Problema na requisicao: ", response.status_code)


if __name__ == "__main__":

    csv_path = ".\\data\\vultr.csv"
    output_csv_path = ".\\out\\vultr_analise.csv"

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    whois = Whois(csv_path, output_csv_path, session)
    whois.verifica_dominios()
