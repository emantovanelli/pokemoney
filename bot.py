import os
import json
import tweepy
import requests
from time import sleep
from decouple import config


def get_dolar():
    cotacoes = requests.get(
        'http://cotacoes.economia.uol.com.br/cambioJSONChart.html?type=d&cod=BRL&mt=off')

    cotacoes_json = json.loads(cotacoes.content)
    dolar_value = "{:.2f}".format(float(cotacoes_json[2]['ask']))
    read_time = cotacoes_json[2]['timestamp']
    return dolar_value, read_time


def get_pokemon(pokemon_id):
    request_pokemon = requests.get(
        'https://pokeapi.co/api/v2/pokemon/{}'.format(pokemon_id))

    qual_e_esse_pokemon = json.loads(request_pokemon._content)
    return qual_e_esse_pokemon['name'].capitalize()


def make_tweet(api, config, data, pokemon_name, pokemon_id):
    if 'dolar_value' in config:
        old_value = config['dolar_value']
        dolar_value = data['dolar_value']

        if float(old_value) < float(dolar_value):
            status_template = "O dólar subiu para R${} :(\n\n #{} - {}"
        elif float(old_value) > float(dolar_value):
            status_template = "O dólar caiu para R${}\n\n #{} - {}"
        else:
            status_template = "Não mudou nada, o dólar ainda está R${}\n\n #{} - {}"
    else:
        status_template = "Quanto tá o pokédólar? R${}\n\n #{} - {}"
    try:
        status = status_template.format(
            data['dolar_value'], pokemon_id, pokemon_name)
        pokemon_sprite = 'sprites/{}.png'.format(pokemon_id)
        api.update_with_media(pokemon_sprite, status)
        config_file = open('config.json', 'w')
        json.dump(data, config_file)
    except Exception as e:
        print(e)


def main():
    consumer_key = config('consumer_key')
    consumer_secret = config('consumer_secret')
    access_token = config('access_token')
    access_token_secret = config('access_token_secret')

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    config_file = open('config.json', 'r')
    config_json = json.load(config_file)
    config_file.close()

    while True:
        data = {}
        data['dolar_value'], data['timestamp'] = get_dolar()

        poke_value = data['dolar_value'].replace('.', '')
        pokemon_name = get_pokemon(poke_value)

        print(pokemon_name)

        make_tweet(api, config_json, data, pokemon_name,
                   poke_value)
        print("Upload is done")

        sleep(10800)  # sleeps for 3 hours


if __name__ == "__main__":
    main()
