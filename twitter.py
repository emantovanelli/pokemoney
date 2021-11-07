import os
import tweepy
from log import log


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
    except Exception as e:
        print(e)


def config_twitter_api():
    consumer_key = os.environ.get("CONSUMER_KEY")
    consumer_secret = os.environ.get("CONSUMER_SECRET")
    access_token = os.environ.get("ACCESS_TOKEN")
    access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    return api
