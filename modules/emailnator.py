import httpx
import re


class Emailnator:
    def __init__(self):
        self.base_url = 'https://www.emailnator.com/'
        self.session = httpx.Client()

        self.session.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Host': 'www.emailnator.com',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0'
        }

        self.session.get(self.base_url)

        del self.session.headers['Sec-Fetch-User']
        del self.session.headers['Upgrade-Insecure-Requests']

        self.session.headers['Accept'] = 'application/json, text/plain, */*'
        self.session.headers['Content-Type'] = 'application/json'
        self.session.headers['Origin'] = self.base_url.rstrip('/')
        self.session.headers['Referer'] = self.base_url
        self.session.headers['Sec-Fetch-Dest'] = 'empty'
        self.session.headers['Sec-Fetch-Mode'] = 'cors'
        self.session.headers['Sec-Fetch-Site'] = 'same-origin'
        self.session.headers['TE'] = 'trailers'
        self.session.headers['X-KL-kfa-Ajax-Request'] = 'Ajax_Request'
        self.session.headers['X-Requested-With'] = 'XMLHttpRequest'
        self.session.headers['X-XSRF-TOKEN'] = str(self.session.cookies['XSRF-TOKEN']).replace('%3D', '=')

    def generate_mail(self, mail_type: list = None):
        mail_json = {'email': ['dotGmail', 'plusGmail'] if mail_type is None else mail_type}
        mail = self.session.post(self.base_url + 'generate-email', json=mail_json).json()['email'][0]
        return mail

    def get_verification_link(self, mail: str):
        while True:
            response = self.session.post(self.base_url + 'message-list', json={'email': mail})
            messges_id = response.json()['messageData']
            total_messeges = len(messges_id)

            for i in range(total_messeges):
                if len(str(messges_id[i]['messageID'])) > 12:
                    messges_id_base = messges_id[i]['messageID']
                    url_email = 'https://www.emailnator.com/message-list'

                    payload = {
                        'email': mail,
                        'messageID': messges_id_base
                    }

                    message = self.session.post(url_email, json=payload)
                    if "https://wl.spotify.com/" in message.text:
                        pattern = re.compile(r'https?://wl\.spotify\.com/ls/click\?.*')
                        verification_url = re.findall(pattern, message.text)[0].split('"')[0]
                        return verification_url
                    else:
                        continue
