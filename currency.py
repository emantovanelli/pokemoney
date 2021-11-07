import json
import requests

def get_dolar():
    cotacoes = requests.get(
        ' https://economia.awesomeapi.com.br/last/USD-BRL')

    cotacoes_json = json.loads(cotacoes.content)
    dolar_value = "{:.2f}".format(float(cotacoes_json['USDBRL']['ask']))
    read_time = cotacoes_json['USDBRL']['timestamp']
    return dolar_value, read_time