import hashlib
import random
from collections import OrderedDict

import requests


class Translator:
    API = 'http://api.fanyi.baidu.com/api/trans/vip/translate'

    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret

    def translate(self, *sentences, from_lang='auto', to_lang='zh'):
        sentence = '\n'.join(sentences)

        salt = random.randint(32768, 65536)
        sign = self.app_id + sentence + str(salt) + self.app_secret

        sign = str(hashlib.md5(sign.encode()).hexdigest())

        dict_ = OrderedDict()
        dict_['appid'] = self.app_id
        dict_['q'] = sentence
        dict_['from'] = from_lang
        dict_['to'] = to_lang
        dict_['salt'] = salt
        dict_['sign'] = sign

        with requests.get(self.API, params=dict_) as resp:
            result = resp.json()['trans_result']

        return tuple(map(lambda x: x['dst'], result))


translator = Translator(app_id='20191106000353533', app_secret='_YLmViRR0gPLva42tX1v')
