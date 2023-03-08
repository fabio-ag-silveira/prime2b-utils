import requests
import json
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
        # df["Titular"] = ""
        # df["Contato Tecnico"] = ""
        # df["Servidor DNS"] = ""
        # df["Status do dominio"] = ""
        # df["Observacao"] = ""

        # for index, row in df.iterrows():

        #     domain = row["Dominio"]
        #     print(f"Dominio: {domain}")

        #     if domain.endswith("br"):
        #         self.dominio_br(domain, df, index)
        #     else:
        #         self.dominio_com(domain, df, index)

        #     df.to_csv(self.output_csv_path, index=False)
        df.fillna("-", inplace=True)
        df.to_csv(self.output_csv_path, index=False)

    def dominio_br(
        self, domain, df, index, api_key="RmiB1MRy21QLOa62PBmuzw==yOWXWsVlftnqJFBE"
    ):

        api_url = f"https://api.api-ninjas.com/v1/whois?domain={domain}"
        response = session.get(api_url, headers={"X-Api-Key": api_key})

        if response.status_code == 200:
            try:
                res = str(response.content).replace("b'", "")[:-1]
                response_json = json.loads(res)
            except:
                response_json = response.json()
            try:
                titular = response_json["registrant_name"]
                nameserver = response_json["name_server"][0]
                contato = response_json["tech_c"]
                df.at[index, "Titular"] = titular
                df.at[index, "Contato Tecnico"] = contato
                df.at[index, "Servidor DNS"] = nameserver
            except Exception:
                print(response_json)
                observacao = "Dominio indisponivel"
                df.at[index, "Observacao"] = observacao
        elif response.status_code == 404:
            observacao = "Recurso inexistente"
            df.at[index, "Observacao"] = observacao
        else:
            print("Problema na requisicao: ", response.status_code)

    def dominio_com(
        self, domain, df, index, api_key="RmiB1MRy21QLOa62PBmuzw==yOWXWsVlftnqJFBE"
    ):

        api_url = f"https://api.api-ninjas.com/v1/whois?domain={domain}"
        response = session.get(api_url, headers={"X-Api-Key": api_key})

        if response.status_code == 200:
            try:
                res = str(response.content).replace("b'", "")[:-1]
                response_json = json.loads(res)
            except:
                response_json = response.json()
            try:
                titular = response_json["name"]
                nameserver = response_json["name_servers"][0]
                df.at[index, "Titular"] = titular
                df.at[index, "Servidor DNS"] = nameserver
            except Exception:
                print(response_json)
                observacao = "Dominio indisponivel"
                df.at[index, "Observacao"] = observacao
        elif response.status_code == 404:
            observacao = "Recurso inexistente"
            df.at[index, "Observacao"] = observacao
        else:
            print("Problema na requisicao: ", response.status_code)


if __name__ == "__main__":

    csv_path = ".\\out\\output.csv"
    output_csv_path = ".\\out\\output.csv"

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    whois = Whois(csv_path, output_csv_path, session)
    whois.verifica_dominios()
