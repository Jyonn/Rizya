import requests

from Base.translator import translator


class IP2Location:
    API = 'http://ip-api.com/json/{0}?fields=status,country,regionName,lat,lon'

    def __init__(self, ip):
        with requests.get(self.API.format(ip)) as resp:
            data = resp.json()  # type: dict

        if data.get('status') == 'success':
            self.country, self.region, self.latitude, self.longitude = \
                data['country'], data['regionName'], data['lat'], data['lon']
        else:
            self.country, self.region, self.latitude, self.longitude = \
                'Unknown', 'Unknown', None, None

        self.political_review()
        self.region_cn, self.country_cn = translator.translate(self.region, self.country)

    def political_review(self):
        if self.country in ['Hong Kong', 'Macao', 'Taiwan']:
            self.region = self.country
            self.country = 'China'
