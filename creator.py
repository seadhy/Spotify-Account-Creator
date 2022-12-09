import httpx, json, os, sqlite3, threading
from random import choice, randint
from time import sleep
from uuid import uuid4
from modules.console import Console,Tools
from modules.faker import Faker

os.system('cls')
os.system('mode 200, 40')


class Gen:
    def __init__(self):
        self.tools = Tools()
        self.tools.printLogo()
        self.faker = Faker()
        self.console = Console()

        self.config_file = json.load(open('data/config.json', 'r', encoding='utf-8'))
        self.settings = self.config_file['settings']
        self.follow_ids = self.config_file['follow_ids']
        self.follow_types = self.config_file['follow_types']
        self.save_methods = self.config_file['save_methods']

        self.client_version = '1.2.1.156.g948cb3fe'  # you can change value to new version

        self.proxies = open('data/proxies.txt', 'r', encoding='utf-8').read().splitlines()
        if len(self.proxies) == 0 and self.settings['Use_Proxy'] == 'y':
            self.settings['Use_Proxy'] = 'n'
            self.console.printe('Continuing without using proxy because there is no proxy in data/proxies.txt folder.')
            sleep(1)

        if self.settings['Threads'] < 1:
            self.settings['Threads'] = 1
            self.console.printe('It continues as thread 1 because the number of threads cannot be less than 1!')
            sleep(1)

        self.connection = sqlite3.connect('saved/database.db', check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS accounts (Account_ID TEXT, Account_Name TEXT, Account_Mail TEXT, Account_Password TEXT, Login_Token TEXT, Bearer_Token TEXT)')

        self.created = 0

        self.tools.setTitle(self.settings['Threads'], len(self.proxies), self.created)

    def getClientToken(self, session: httpx.Client) -> str:

        payload = {
        	"client_data": {
        		"client_id": "d8a5ed958d274c2e8ee717e6a4b0971d",
        		"client_version": self.client_version,
        		"js_sdk_data": {
        			"device_brand": "unknown",
        			"device_model": "desktop",
        			"os": "Windows",
        			"os_version": "NT 10.0"
        		}
        	}
        }

        headers = {
            "Host": "clienttoken.spotify.com",
            "Accept": "application/json",
            "Accept-Language": "tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "Content-Length": str(len(json.dumps(payload))),
            "Origin": "https://open.spotify.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Referer": "https://open.spotify.com/",
            "Connection": "keep-alive",
            "TE": "trailers"
        }


        r = session.post(url='https://clienttoken.spotify.com/v1/clienttoken', headers=headers, json=payload)
        if r.status_code == 200:
            return r.json()['granted_token']['token']

    def getCsrfToken(self, session: httpx.Client) -> str:
        headers = {
            "Host": "www.spotify.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "TE": "trailers"
        }

        r = session.get(url='https://www.spotify.com/us/signup', headers=headers)

        if r.status_code == 200:
            return r.text.split('csrfToken')[1].split('"')[2]

    def getToken(self, session: httpx.Client, login_token: str) -> str:
        headers = {
            "Host": "www.spotify.com",
            "Accept": "*/*",
            "Accept-Language": "tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.spotify.com/us/signup?forward_url=https%3A%2F%2Fopen.spotify.com%2F",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRF-Token": self.getCsrfToken(session),
            "X-KL-Ajax-Request": "Ajax_Request",
            "Content-Length": "28",
            "Origin": "https://www.spotify.com",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "TE": "trailers"
        }

        r1 = session.post(url='https://www.spotify.com/api/signup/authenticate', headers=headers, data=f'splot={login_token}')

        if r1.status_code == 200:
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "spotify-app-version": self.client_version,
                "app-platform": "WebPlayer",
                "Host": "open.spotify.com",
                "Referer": "https://open.spotify.com/",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "TE": "trailers"
            }

            r2 = session.get(url='https://open.spotify.com/get_access_token?reason=transport&productType=web_player', headers=headers)
            if r2.status_code == 200:
                return r2.json()['accessToken']

    def followAccount(self, session: httpx.Client, client_token: str, token: str):
        while True:
            for account_id in self.follow_ids["Account_IDs"]:
                try:
                    headers = {
                        "Host": "api.spotify.com",
                        "Accept": "application/json",
                        "Accept-Language": "tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3",
                        "Accept-Encoding": "gzip, deflate, br",
                        "app-platform": "WebPlayer",
                        "spotify-app-version": self.client_version,
                        "client-token": client_token,
                        "Origin": "https://open.spotify.com",
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-site",
                        "authorization": f"Bearer {token}",
                        "Referer": "https://open.spotify.com/",
                        "Connection": "keep-alive",
                        "Content-Length": "0",
                        "TE": "trailers"
                    }

                    r = session.put(url=f'https://api.spotify.com/v1/me/following?type=user&ids={account_id}', headers=headers)

                    if r.status_code == 204:
                        self.console.printi(f'Successfully followed to account: [{account_id}]')
                    else:
                        self.console.printe('Error following account. Retrying...')
                except Exception:
                    self.console.printe('Error following account. Retrying...')
                    continue
            break

    def changeAvatar(self, session: httpx.Client, client_token: str, token: str, account_id: str):
        while True:
            try:
                avatar = self.faker.getAvatar()

                headers = {
                    "Host": "image-upload.spotify.com",
                    "Accept": "application/json",
                    "Accept-Language": "tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Content-Type": "image/jpeg",
                    "client-token": client_token,
                    "Origin": "https://open.spotify.com",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-site",
                    "authorization": f"Bearer {token}",
                    "Referer": "https://open.spotify.com/",
                    "Connection": "keep-alive",
                    "TE": "trailers"
                }

                r1 = session.post(url='https://image-upload.spotify.com/v4/user-profile', headers=headers, data=avatar)

                if r1.status_code == 200:
                    upload_token = r1.json()['uploadToken']

                    headers = {
                        'Accept': 'application/json',
                        'Accept-Language': 'tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'app-platform': 'WebPlayer',
                        'spotify-app-version': self.client_version,
                        'client-token': client_token,
                        'Origin': 'https://open.spotify.com',
                        'Sec-Fetch-Dest': 'empty',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Site': 'same-site',
                        'authorization': f'Bearer {token}',
                        'Referer': 'https://open.spotify.com/',
                        'Connection': 'keep-alive',
                        'Content-Length': '0',
                        'TE': 'trailers',
                    }

                    r2 = session.post(url=f'https://spclient.wg.spotify.com/identity/v3/profile-image/{account_id}/{upload_token}', headers=headers)
                    if r2.status_code == 200:
                        self.console.printhc('Successfully pfp changed.')
                        break
                    else:
                        self.console.printe('Error changing pfp. Retrying...')
            except Exception:
                self.console.printe('Error changing pfp. Retrying...')

    def followPlaylist(self, session: httpx.Client, client_token: str, token: str):
        while True:
            try:
                for playlist_id in self.follow_ids["Playlist_IDs"]:
                    headers = {
                        'Accept': 'application/json',
                        'Accept-Language': 'tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Content-Type': 'application/json;charset=UTF-8',
                        'app-platform': 'WebPlayer',
                        'spotify-app-version': self.client_version,
                        'client-token': client_token,
                        'Origin': 'https://open.spotify.com',
                        'Sec-Fetch-Dest': 'empty',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Site': 'same-site',
                        'authorization': f'Bearer {token}',
                        'Referer': 'https://open.spotify.com/',
                        'Connection': 'keep-alive',
                        'TE': 'trailers'
                    }

                    r = session.put(url=f'https://api.spotify.com/v1/playlists/{playlist_id}/followers', headers=headers)
                    if r.status_code == 200:
                        self.console.printi(f'Successfully followed to playlist: [{playlist_id}]')
                    else:
                        self.console.printe('Error following, retrying...')
            except Exception:
                self.console.printe('Error following, Retrying...')
                continue
            break
    def followArtist(self, session: httpx.Client, client_token: str, token: str):
        while True:
            try:
                for artist_id in self.follow_ids["Artist_IDs"]:
                    headers = {
                        "Host": "api.spotify.com",
                        "Accept": "application/json",
                        "Accept-Language": "tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3",
                        "Accept-Encoding": "gzip, deflate, br",
                        "app-platform": "WebPlayer",
                        "spotify-app-version": self.client_version,
                        "client-token": client_token,
                        "Origin": "https://open.spotify.com",
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-site",
                        "authorization": f"Bearer {token}",
                        "Referer": "https://open.spotify.com/",
                        "Connection": "keep-alive",
                        "Content-Length": "0",
                        "TE": "trailers"
                    }

                    r = session.put(url=f'https://api.spotify.com/v1/me/following?type=artist&ids={artist_id}', headers=headers)

                    if r.status_code == 204:
                        self.console.printi(f'Successfully followed to artist account: [{artist_id}]')
                    else:
                        self.console.printe('Error following artist account. Retrying...')
                        print(r.text)
            except Exception:
                self.console.printe('Error following artist account. Retrying...')
                continue

            break

    def createAccount(self):
        while True:
            try:
                if self.settings['Use_Proxy'] == 'y':
                    proxy = choice(self.proxies)
                    session = httpx.Client(headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"}, proxies={"http://": f"http://{proxy}","https://": f"http://{proxy}"})
                else:
                    session = httpx.Client(headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"})
                username = self.faker.getUsername(self.settings['Create_Username'])
                mail = self.faker.getMail(16)
                password = self.faker.getPassword(12)
                birthday = self.faker.getBirthday()

                payload = {
                	"account_details": {
                		"birthdate": birthday,
                		"consent_flags": {
                			"eula_agreed": True,
                			"send_email": True,
                			"third_party_email": True
                		},
                		"display_name": username,
                		"email_and_password_identifier": {
                			"email": mail,
                			"password": password
                		},
                		"gender": randint(1, 2)
                	},
                	"callback_uri": "https://www.spotify.com/signup/challenge?locale=us",
                	"client_info": {
                		"api_key": "a1e486e2729f46d6bb368d6b2bcda326",
                		"app_version": "v2",
                		"capabilities": [
                			1
                		],
                		"installation_id": str(uuid4()),
                		"platform": "www"
                	},
                	"tracking": {
                		"creation_flow": "",
                		"creation_point": "https://www.spotify.com/uk/",
                		"referrer": ""
                	}
                }

                headers = {
                    "Host": "spclient.wg.spotify.com",
                    "Accept": "*/*",
                    "Accept-Language": "tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Referer": "https://www.spotify.com/",
                    "Content-Type": "application/json",
                    "Content-Length": str(len(json.dumps(payload))),
                    "Origin": "https://www.spotify.com",
                    "Connection": "keep-alive",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-site",
                    "TE": "trailers"
                }

                r = session.post(url='https://spclient.wg.spotify.com/signup/public/v2/account/create', headers=headers, json=payload, timeout=15)

                if r.status_code == 200:
                    self.console.printsc(f'Account has been created with the name {username}.')
                    self.created += 1
                    self.tools.setTitle(self.settings['Threads'], len(self.proxies), self.created)
                    account_id = r.json()['success']['username']
                    login_token = r.json()['success']['login_token']
                    client_token = self.getClientToken(session)
                    token = self.getToken(session, login_token)

                    if self.settings['Change_Avatar'] == 'y':
                        self.changeAvatar(session, client_token, token, account_id)


                    if self.follow_types['Profile'] == 'y':
                        self.followAccount(session, client_token, token)

                    if self.follow_types['Playlist'] == 'y':
                        self.followPlaylist(session, client_token, token)

                    if self.follow_types['Artist'] == 'y':
                        self.followArtist(session, client_token, token)

                    if self.save_methods['Text_File'] == 'y':
                        with open('saved/accounts.txt', 'a', encoding='utf-8') as f:
                            f.write(f"{username}:{mail}:{password}\n")
                        with open('saved/tokens.txt', 'a', encoding='utf-8') as f:
                            f.write(f"{token}\n")

                    if self.save_methods['SQLite'] == 'y':
                        self.cursor.execute('Insert into accounts Values(?,?,?,?,?,?)', (account_id, username, mail, password, login_token, token))
                        self.connection.commit()

                elif 'VPN' in r.text:
                    self.console.printe(f'Account not created. Bad proxies: {proxy}')
                    # self.proxies.remove(proxy)
                else:
                    self.console.printe('Account not created.')
                    # print(payload)
                    # print(r.text)
            except Exception as e:
                self.console.printe(f'{str(e).capitalize()}. Retrying...')
                continue

    def start(self):
        while threading.active_count() < self.settings['Threads'] + 1:
            threading.Thread(target=self.createAccount).start()



if __name__ == '__main__':
    gen = Gen()
    gen.start()
