import httpx
import json
import re
from time import sleep
from random import choices
from string import ascii_lowercase, digits, ascii_letters
from modules.console import Console


class Mail:
    def __init__(self) -> None:
        self.console = Console()

        self.generate_url = 'https://api.mail.tm/accounts'
        self.token_url = 'https://api.mail.tm/token'
        self.messages_url = 'https://api.mail.tm/messages'

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0', 'Accept': 'application/ld+json', 'Accept-Language': 'tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3', 'Accept-Encoding': 'gzip, deflate, br', 'Referer': 'https://api.mail.tm/domains', 'X-KL-saas-Ajax-Request': 'Ajax_Request', 'Connection': 'keep-alive', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin', 'If-None-Match': '5dea09b3c8649bf068660601a9ef0f1e', 'TE': 'trailers'}

        try:
            self.domain = httpx.get('https://api.mail.tm/domains?page=1', headers=headers, timeout=10).json()['hydra:member'][0]['domain']
        except Exception:
            self.domain = 'exelica.com'

    def generateMail(self, proxies = None) -> tuple:
        while True:
            try:
                mail_text = ''.join(choices(ascii_lowercase + digits, k=12))
                mail = f'{mail_text}@{self.domain}'
                password = ''.join(choices(ascii_letters + digits, k=12))

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Content-Type': 'application/json',
                    'Referer': 'https://mail.tm/',
                    'Origin': 'https://mail.tm',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-site',
                    'Connection': 'keep-alive',
                    'TE': 'trailers',
                }

                payload = {
                    "address": mail,
                    "password": password
                }

                r = httpx.post(url=self.generate_url, headers=headers, json=payload, proxies=proxies, timeout=30)
                if r.status_code == 201:
                    try:
                        auth_token = httpx.post(url=self.token_url, json=payload, proxies=proxies, timeout=30).json()

                        return mail, password, auth_token['token']
                    except json.decoder.JSONDecodeError:
                        sleep(3)
                        continue
                elif r.status_code == 422:
                    self.console.printe('Generation Error: already used mail address.')
            except Exception as e:
                self.console.printe('Generation Error: ' + str(e).capitalize() + '.')
                continue

    def getVerificationLink(self, token: str, proxies = None) -> str:
        while True:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Referer': 'https://mail.tm/',
                    'Origin': 'https://mail.tm',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-site',
                    'Authorization': f"Bearer {token}",
                    'Connection': 'keep-alive',
                    'TE': 'trailers',
                }

                r = httpx.get('https://api.mail.tm/messages', headers=headers, proxies=proxies, timeout=30)

                if r.json()['hydra:totalItems'] > 0:
                    r = httpx.get('https://api.mail.tm/messages/' + r.json()['hydra:member'][0]['id'], headers=headers)
                    verification_link = re.search('https://wl.spotify.com/ls/click\?upn=.*', r.json()['text'])[0].rstrip(' )')

                    return verification_link

                sleep(1)
            except IndexError:
                sleep(1)
                continue
            except json.decoder.JSONDecodeError:
                sleep(3)
                continue
            except Exception as e:
                self.console.printe('Verification Error: ' + str(e).capitalize() + '.')
                continue
