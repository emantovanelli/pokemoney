import os
import json
import tweepy
import requests
from log import log
from time import sleep
from os.path import exists


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


def get_pokemon(pokemon_id):
    log('getting pokemon')
    request_pokemon = requests.get(
        'https://pokeapi.co/api/v2/pokemon/{}'.format(pokemon_id))

    qual_e_esse_pokemon = json.loads(request_pokemon._content)

    log('getting {} sprite'.format(qual_e_esse_pokemon['name']))
    path = get_pokemon_sprite(pokemon_id, qual_e_esse_pokemon['sprites'])
    return qual_e_esse_pokemon['name'].capitalize(), path
