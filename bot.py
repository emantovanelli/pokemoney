import os
import json
import tweepy
import requests
import sys
from time import sleep
from os.path import exists
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler(timezone="america/sao_paulo")


def log(message):
    print(message)
    sys.stdout.flush()

def get_dolar():
    cotacoes = requests.get(
        ' https://economia.awesomeapi.com.br/last/USD-BRL')

    cotacoes_json = json.loads(cotacoes.content)
    dolar_value = "{:.2f}".format(float(cotacoes_json['USDBRL']['ask']))
    read_time = cotacoes_json['USDBRL']['timestamp']
    return dolar_value, read_time

def get_pokemon_sprite(pokemon_id, pokemon_sprites):
    path = 'sprites/' + str(pokemon_id) + '.png'
    file_exists = exists(path)
    if not file_exists:
        log('pokemon sprite does not exists')
        with open(path, 'wb') as handler:
            img_data = requests.get(
                pokemon_sprites['other']['official-artwork']['front_default']).content
            if img_data is None:
                img_data = requests.get(pokemon_sprites['front-default']).content
            handler.write(img_data)
            handler.close()
    return path

def get_pokemon(pokemon_id):
    log('getting pokemon')
    request_pokemon = requests.get(
        'https://pokeapi.co/api/v2/pokemon/{}'.format(pokemon_id))

    qual_e_esse_pokemon = json.loads(request_pokemon._content)

    log('getting {} sprite'.format(qual_e_esse_pokemon['name']))
    path = get_pokemon_sprite(pokemon_id, qual_e_esse_pokemon['sprites'])
    return qual_e_esse_pokemon['name'].capitalize(), path

def get_pokemons_sprite(range_min, range_max):
    for i in range(range_max, range_min, -1):
        path = 'sprites/' + str(i) + '.png'
        file_exists = exists(path)
        if not file_exists:
            log('Baixando infos do pokemon: ' + str(i))
            request_pokemon = requests.get(
                'https://pokeapi.co/api/v2/pokemon/{}'.format(i))

            qual_e_esse_pokemon = json.loads(request_pokemon._content)
            log('Infos do {} baixadas'.format(qual_e_esse_pokemon['name']))

            with open(path, 'wb') as handler:
                log('Baixando imagem do {}'.format(qual_e_esse_pokemon['name']))

                if qual_e_esse_pokemon['sprites']['other']['official-artwork']['front_default'] is not None:
                    img_data = requests.get(
                        qual_e_esse_pokemon['sprites']['other']['official-artwork']['front_default']).content
                else:
                    img_data = requests.get(qual_e_esse_pokemon['sprites']['front-default']).content
                handler.write(img_data)
                handler.close()
                log('Imagem do {} baixada'.format(qual_e_esse_pokemon['name']))
        sleep(1)

def make_tweet(api, config, data, pokemon_name, pokemon_id, pokemon_sprite_path):
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

        log('uploading media')
        media = api.media_upload(filename=pokemon_sprite_path, file=open(pokemon_sprite_path, 'rb'))
        log('media uploaded')
        log('sending tweet')

        tweet_result = api.update_status(status=status, media_ids=[media.media_id])
        log('tweet was sent')



        config_file = open('config.json', 'w')
        json.dump(data, config_file)
    except Exception as e:
        print(e)

def config_api():
    consumer_key = os.environ.get("CONSUMER_KEY")
    consumer_secret = os.environ.get("CONSUMER_SECRET")
    access_token = os.environ.get("ACCESS_TOKEN")
    access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    return api

@sched.scheduled_job('interval', hours=3)
def main():
    api = config_api()
    log('API configured')


    config_file = open('config.json', 'r')
    config_json = json.load(config_file)
    config_file.close()

    data = {}
    data['dolar_value'], data['timestamp'] = get_dolar()

    poke_value = data['dolar_value'].replace('.', '')
    pokemon_name, sprite_path = get_pokemon(poke_value)

    log('pokemon: {}'.format(pokemon_name))

    make_tweet(api, config_json, data, pokemon_name,
               poke_value, sprite_path)


# if __name__ == "__main__":
#     main()

sched.start()
