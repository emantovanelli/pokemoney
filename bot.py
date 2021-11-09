import json
from time import sleep
from log import log
from currency import get_dolar
from local_dropbox import get_document, save_document
from pokemon import get_pokemon
from twitter import config_twitter_api, make_tweet
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler(timezone="america/sao_paulo")


@sched.scheduled_job('interval', hours=3)
def main():
    api = config_twitter_api()
    log('API configured')

    try:
        get_document('config.json')
        document = open('config.json', 'r')

        config_json = json.load(document)
        document.close()
    except Exception as e:
        print(e)

    data = {}
    data['dolar_value'], data['timestamp'] = get_dolar()

    log('dolar value: {}'.format(data['dolar_value']))

    config_file = open('config.json', 'w')
    json.dump(data, config_file)
    config_file.close()

    save_document('config.json')

    poke_value = data['dolar_value'].replace('.', '')
    pokemon_name, sprite_path = get_pokemon(poke_value)

    log('pokemon: {}'.format(pokemon_name))

    for tentativa in range(3):
        try:
            make_tweet(api, config_json, data, pokemon_name,
                       poke_value, sprite_path)
        except Exception as e:
            sleep(60)
            print(e)
        else:
            break
    else:
        log('make tweet error even with retries')



    config_file = open('config.json', 'w')
    json.dump(data, config_file)
    config_file.close()


#
# if __name__ == '__main__':
#     main()
#

sched.start()
