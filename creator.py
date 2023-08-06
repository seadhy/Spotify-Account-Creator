try:
    import httpx
    import sys
    import json
    import sqlite3
    import threading
    from time import sleep
    from uuid import uuid4
    from cursor import hide
    from subprocess import call
    from random import choice, randint
    from modules.console import Console, Tools
    from modules.faker import Faker
    from modules.mail_service import Mail
    from modules.emailnator import Emailnator
except ModuleNotFoundError:
    print('Modules not found! Please run `install.bat` and restart the tool.')
    input()
    exit()

if sys.platform == 'win32':
    hide()
    call('cls', shell=True)
    call('mode 200, 40', shell=True)
else:
    call('clear', shell=True)

lock = threading.Lock()


def checkVersion() -> bool:
    r = httpx.get('https://raw.githubusercontent.com/seadhy/Spotify-Account-Creator/main/modules/__version__.py')
    if r.status_code == 200:
        global_data = dict()
        local_data = dict()

        exec(r.text, global_data)

        with open('modules/__version__.py', 'r', encoding='utf-8') as f:
            exec(f.read(), local_data)

        if local_data['__version__'] == global_data['__version__']:
            return True
        else:
            return False
    else:
        return True


class Gen:
    def __init__(self):
        self.tools = Tools()
        self.tools.printLogo()
        self.faker = Faker()
        self.console = Console()
        self.mail_tm = Mail()
        
        
        try:
            self.config_file = json.load(open('data/config.json', 'r', encoding='utf-8'))
        except json.decoder.JSONDecodeError as e:
            self.console.printe(f'Failed to read config file! Please fix this part: {str(e).split(":")[1].strip().capitalize()}.')
            exit()
            
        self.settings = self.config_file['settings']
        self.verification_settings = self.config_file['verification_settings']
        self.target_settings = self.config_file['target_settings']
        self.follow_ids = self.config_file['follow_ids']
        self.follow_types = self.config_file['follow_types']
        self.save_methods = self.config_file['save_methods']
        self.mail_services = list()

        for service in self.config_file['verification_settings']['Services'].keys():
            self.mail_services.append(service) if self.config_file['verification_settings']['Services'][service] == 'y' else None


        self.client_version = '1.2.18.564.g83d531e5'  # you can change value to new version

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
        
    @staticmethod
    def debugMode(*args):
        lock.acquire()
        print('----------DEBUG------------')
        for _ in args:
            print(_)
        print('----------DEBUG------------')
        lock.release()

    def getClientToken(self, session: httpx.Client) -> str:
        while True:
            payload = {
                'client_data': {
                    'client_version': self.client_version,
                    'client_id': 'd8a5ed958d274c2e8ee717e6a4b0971d',
                    'js_sdk_data': {
                        'device_brand': 'unknown',
                        'device_model': 'unknown',
                        'os': 'windows',
                        'os_version': 'NT 10.0',
                        'device_id': str(uuid4()),
                        'device_type': 'computer'
                    }
                }
            }

            headers = {
                'authority': 'clienttoken.spotify.com',
                'accept': 'application/json',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/json',
                'origin': 'https://open.spotify.com',
                'referer': 'https://open.spotify.com/',
                'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
            }

            r = session.post(url='https://clienttoken.spotify.com/v1/clienttoken', headers=headers, json=payload)
            
            if r.status_code == 200:
                return r.json()['granted_token']['token']
            else:
                self.console.printe('Failed to get Client Token. Retrying...')
                if self.settings['Debug_Mode'] == 'y':
                    self.debugMode(r.text, r.status_code)

    def getCsrfToken(self, session: httpx.Client) -> str:
        while True:
            headers = {
                'authority': 'www.spotify.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US,en;q=0.9',
                'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
            }

            r = session.get(url='https://www.spotify.com/us/signup', headers=headers)

            if r.status_code == 200:
                return r.text.split('csrfToken')[1].split('"')[2]
            else:
                self.console.printe('Failed to get CSRF-Token. Retrying...')
                if self.settings['Debug_Mode'] == 'y':
                    self.debugMode(r.text, r.status_code)

    def getToken(self, session: httpx.Client, login_token: str) -> str:
        while True:   
            headers = {
                'authority': 'www.spotify.com',
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://www.spotify.com',
                'referer': 'https://www.spotify.com/us/signup',
                'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'x-csrf-token': self.getCsrfToken(session),
            }

            r1 = session.post(url='https://www.spotify.com/api/signup/authenticate', headers=headers, data=f'splot={login_token}')

            if r1.status_code == 200:
                headers = {
                    'authority': 'open.spotify.com',
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-language': 'en-US,en;q=0.9',
                    'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'none',
                    'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                }

                r2 = session.get(url='https://open.spotify.com/get_access_token?reason=transport&productType=web_player', headers=headers)
                if r2.status_code == 200:
                    return r2.json()['accessToken']
                else:
                    self.console.printe('Failed to get Access Token. Retrying...')
                    if self.settings['Debug_Mode'] == 'y':
                        self.debugMode(r2.text, r2.status_code)
            else:
                self.console.printe('Failed to authenticating account. Retrying...')
                if self.settings['Debug_Mode'] == 'y':
                    self.debugMode(r1.text, r1.status_code)

    def followAccount(self, session: httpx.Client, client_token: str, token: str):
        while True:
            for account_id in self.follow_ids["Account_IDs"]:
                try:  
                    headers = {
                        'authority': 'api.spotify.com',
                        'accept': 'application/json',
                        'accept-language': 'en',
                        'app-platform': 'WebPlayer',
                        'authorization': f'Bearer {token}',
                        'client-token': client_token,
                        'origin': 'https://open.spotify.com',
                        'referer': 'https://open.spotify.com/',
                        'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"',
                        'sec-fetch-dest': 'empty',
                        'sec-fetch-mode': 'cors',
                        'sec-fetch-site': 'same-site',
                        'spotify-app-version': self.client_version,
                    }

                    r = session.put(url=f'https://api.spotify.com/v1/me/following?type=user&ids={account_id}', headers=headers)

                    if r.status_code == 204:
                        self.console.printi(f'Successfully followed to account: [{account_id}]')
                    else:
                        self.console.printe('Error following account. Retrying...')
                        if self.settings['Debug_Mode'] == 'y':
                            self.debugMode(r.text, r.status_code)
                except Exception:
                    self.console.printe('Error following account. Retrying...')
                    continue
            break

    def changeAvatar(self, session: httpx.Client, client_token: str, token: str, account_id: str):
        while True:
            try:
                avatar = self.faker.getAvatar(self.settings['Create_Avatar'])
                
                headers = {
                    'authority': 'image-upload.spotify.com',
                    'accept': 'application/json',
                    'accept-language': 'en',
                    'authorization': f'Bearer {token}',
                    'client-token': client_token,
                    'content-type': 'image/jpeg',
                    'origin': 'https://open.spotify.com',
                    'referer': 'https://open.spotify.com/',
                    'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-site',
                }


                r1 = session.post(url='https://image-upload.spotify.com/v4/user-profile', headers=headers, data=avatar)

                if r1.status_code == 200:
                    upload_token = r1.json()['uploadToken']

                    headers = {
                        'Accept': 'application/json',
                        'Accept-Language': 'en-US,en;q=0.9',
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
                        'Connection': 'keep-alive'
                    }

                    r2 = session.post(url=f'https://spclient.wg.spotify.com/identity/v3/profile-image/{account_id}/{upload_token}',headers=headers)
                    if r2.status_code == 200:
                        self.console.printhc('Successfully pfp changed.')
                        break
                    else:
                        self.console.printe('Error changing pfp. Retrying...')
                        if self.settings['Debug_Mode'] == 'y':
                            self.debugMode(r2.text, r2.status_code)
                else:
                    self.console.printe('Error uploading pfp. Retrying...')
                    if self.settings['Debug_Mode'] == 'y':
                        self.debugMode(r1.text, r1.status_code)
            except Exception:
                self.console.printe('Error changing pfp. Retrying...')

    def followPlaylist(self, session: httpx.Client, client_token: str, token: str):
        while True:
            try:
                for playlist_id in self.follow_ids['Playlist_IDs']:
                    headers = {
                        'authority': 'api.spotify.com',
                        'accept': 'application/json',
                        'accept-language': 'en',
                        'app-platform': 'WebPlayer',
                        'authorization': f'Bearer {token}',
                        'client-token': client_token,
                        'origin': 'https://open.spotify.com',
                        'referer': 'https://open.spotify.com/',
                        'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"',
                        'sec-fetch-dest': 'empty',
                        'sec-fetch-mode': 'cors',
                        'sec-fetch-site': 'same-site',
                        'spotify-app-version': self.client_version,
                    }

                    r = session.put(url=f'https://api.spotify.com/v1/playlists/{playlist_id}/followers',
                                    headers=headers)
                    if r.status_code == 200:
                        self.console.printi(f'Successfully followed to playlist: [{playlist_id}]')
                    else:
                        self.console.printe('Error following, retrying...')
                        if self.settings['Debug_Mode'] == 'y':
                            self.debugMode(r.text, r.status_code)
            except Exception:
                self.console.printe('Error following, retrying...')
                continue
            break

    def followArtist(self, session: httpx.Client, client_token: str, token: str):
        while True:
            try:
                for artist_id in self.follow_ids['Artist_IDs']:
                    headers = {
                        'authority': 'api.spotify.com',
                        'accept': 'application/json',
                        'accept-language': 'en',
                        'app-platform': 'WebPlayer',
                        'authorization': f'Bearer {token}',
                        'client-token': client_token,
                        'origin': 'https://open.spotify.com',
                        'referer': 'https://open.spotify.com/',
                        'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"',
                        'sec-fetch-dest': 'empty',
                        'sec-fetch-mode': 'cors',
                        'sec-fetch-site': 'same-site',
                        'spotify-app-version': self.client_version,
                    }
                    
                    r = session.put(url=f'https://api.spotify.com/v1/me/following?type=artist&ids={artist_id}', headers=headers)

                    if r.status_code == 204:
                        self.console.printi(f'Successfully followed to artist account: [{artist_id}]')
                    else:
                        self.console.printe('Error following artist account. Retrying...')
                        if self.settings['Debug_Mode'] == 'y':
                            self.debugMode(r.text, r.status_code)
            except Exception:
                self.console.printe('Error following artist account. Retrying...')
                continue

            break

    def verifyMail(self, session: httpx.Client, verification_link: str):
        while True:
            try:
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1',
                    'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"'
                }
                
                r = session.get(verification_link, headers=headers, follow_redirects=True)


                if r.status_code == 200:
                    
                    url = str(r.url)
                    verification_token = url.split('?t=')[1].split('&')[0]
                                        
                    headers = {
                        'authority': 'www.spotify.com',
                        'accept': '*/*',
                        'accept-language': 'en-US,en;q=0.9',
                        'content-type': 'text/plain;charset=UTF-8',
                        'origin': 'https://www.spotify.com',
                        'referer': url,
                        'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"',
                        'sec-fetch-dest': 'empty',
                        'sec-fetch-mode': 'cors',
                        'sec-fetch-site': 'same-origin'
                    }

                    payload = {'token': verification_token}

                    r = session.post('https://www.spotify.com/api/email-verify/v1/verify',  headers=headers, json=payload)
                                                                                    
                    if r.json()['success']:
                        self.console.printmf(verification_link[:150] + '...')
                        break
                    else:
                        if self.settings['Debug_Mode'] == 'y':
                            self.debugMode(r.text, r.status_code)
                else:
                    self.console.printe('Error opening link, retrying...')
                    if self.settings['Debug_Mode'] == 'y':
                        self.debugMode(r.text, r.status_code)
            except Exception as e:
                self.console.printe('Error mail verification, retrying...')
                if self.settings['Debug_Mode'] == 'y':
                    self.debugMode(str(e))

    
    def bypassChallenge(self, session: httpx.Client, client_token: str, client_id: str, session_id: str, proxy: str = None):
        while True:
            try:
                payload = {'session_id': session_id}

                headers = {
                    'accept': 'application/json',
                    'accept-encoding': 'gzip',
                    'accept-language': 'en-US',
                    'app-platform': 'Android',
                    'client-token': client_token,
                    'connection': 'Keep-Alive',
                    'content-type': 'application/json',
                    'host': 'spclient.wg.spotify.com',
                    'spotify-app-version': '8.8.56.538',
                    'user-agent': 'Spotify/8.8.56.538 Android/28 (SM-S908E)',
                    'x-client-id': client_id
                }

                r = session.post('https://spclient.wg.spotify.com/challenge-orchestrator/v1/get-session',headers=headers, json=payload)


                if r.status_code == 200:

                    url = str(r.url)               

                    challenge_url: str = r.json()['in_progress']['challenge_details']['web_challenge_launcher']['url']
                    challenge_id = challenge_url.split('/')[-2]


                    headers = {
                        'authority': 'challenge.spotify.com',
                        'accept': 'application/json',
                        'accept-language': 'en-US,en;q=0.9',
                        'content-type': 'application/json',
                        'origin': 'https://challenge.spotify.com',
                        'referer': url,
                        'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"',
                        'sec-fetch-dest': 'empty',
                        'sec-fetch-mode': 'cors',
                        'sec-fetch-site': 'same-origin',
                    }  

                    if challenge_url.endswith('recaptcha'):
                        self.console.printe(f'Account not created. Recaptcha challenges cannot be solved at this time. If you are constantly getting this error, try again with quality proxies.')
                        break
                    elif challenge_url.endswith('dummy'):
                        payload = {
                           'session_id': session_id,
                           'challenge_id': challenge_id,
                           'dummy_challenge_v1': {'noop': {}}
                        }
                    else:
                        self.console.printe(f'Account not created. Error: {r.text}')

                    r = session.post('https://challenge.spotify.com/api/v1/invoke-challenge-command', headers=headers, json=payload)
                    if r.status_code == 200:
                        r = httpx.post('https://spclient.wg.spotify.com/signup/public/v2/account/complete-creation', headers=headers, json={'session_id': session_id})
                        if r.status_code == 200 and 'success' in r.text:
                            return r.json()['success']
                        else:
                            self.console.printe('Failed bypassing challenge. Retrying...')
                            if self.settings['Debug_Mode'] == 'y':
                                self.debugMode(r.text, r.status_code)
            except Exception as e:
                self.console.printe('Error bypassing, retrying...')
                if self.settings['Debug_Mode'] == 'y':
                    self.debugMode(str(e))
                continue

    def createAccount(self, session: httpx.Client, username: str, mail: str, password: str, client_token: str, inbox, emailnator, account_data: dict):
        while True:
            try:
                self.console.printsc(f'Account has been created with the name {username}.')

                if self.verification_settings['Verify_Mail'] == 'y':
                    if not ('@gmail.com' in mail):
                        verification_link = self.mail_tm.getVerificationLink(inbox[2])
                    else:
                        verification_link = emailnator.get_verification_link(mail)

                    self.verifyMail(session, verification_link)

                account_id = account_data['username']
                login_token = account_data['login_token']

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
                        f.write(f'{username}:{mail}:{password}\n')   
                    with open('saved/tokens.txt', 'a', encoding='utf-8') as f:
                        f.write(f'{token}\n')

                if self.save_methods['SQLite'] == 'y':
                     self.cursor.execute('Insert into accounts Values(?,?,?,?,?,?)', (account_id, username, mail, password, login_token, token))
                     self.connection.commit()

                break
            
            except Exception as e:
                self.console.printe('Error humanization, retrying...')
                if self.settings['Debug_Mode'] == 'y':
                    self.debugMode(str(e))
                continue
    def main(self):
        while (self.target_settings['Use_Target'] == 'y' and Console.created < self.target_settings['Target_To']) or (
                self.target_settings['Use_Target'] != 'y'):
            try:
                if self.settings['Use_Proxy'] == 'y':
                    proxy = choice(self.proxies)
                    print(proxy)
                    proxies = {'http://': f'http://{proxy}', 'https://': f'http://{proxy}'}
                    session = httpx.Client(headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}, proxies=proxies, timeout=30)
                else:
                    session = httpx.Client(headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}, timeout=30)
                username = self.faker.getUsername(self.settings['Create_Username'])

                if self.verification_settings['Verify_Mail'] == 'y':
                    if choice(self.mail_services) == 'Use_MailTM':
                        inbox = self.mail_tm.generateMail(proxies=proxies if self.settings['Use_Proxy'] == 'y' else None)
                        mail = inbox[0]
                    else:
                        emailnator = Emailnator()
                        mail = emailnator.generate_mail()
                else:
                    mail = self.faker.getMail(16)

                password = self.faker.getPassword(12)
                birthday = self.faker.getBirthday()

                client_token = self.getClientToken(session)
                
                client_id = str(uuid4()).replace('-', '')
                
                payload = {
                    'account_details': {
                        'birthdate': birthday,
                        'consent_flags': {'eula_agreed': True, 'send_email': True, 'third_party_email': True},
                        'display_name': username,
                        'email_and_password_identifier': {'email': mail, 'password': password},
                        'gender': randint(1, 2)
                    },
                    'callback_uri': 'https://auth-callback.spotify.com/r/android/music/signup',
                    'client_info': {
                        'api_key': '142b583129b2df829de3656f9eb484e6',
                        'app_version': '8.8.56.538',
                        'capabilities': [1],
                        'installation_id': str(uuid4()),
                        'platform': 'Android-ARM'
                    },
                    'tracking': {
                        'creation_flow': '',
                        'creation_point': 'client_mobile',
                        'referrer': ''
                    }
                }
                
                
                headers = {
                    'accept': 'application/json',
                    'accept-encoding': 'gzip',
                    'accept-language': 'en-US',
                    'app-platform': 'Android',
                    'client-token': client_token,
                    'connection': 'Keep-Alive',
                    'content-type': 'application/json',
                    'host': 'spclient.wg.spotify.com',
                    'spotify-app-version': '8.8.56.538',
                    'user-agent': 'Spotify/8.8.56.538 Android/28 (SM-S908E)',
                    'x-client-id': client_id
                }

                r = session.post(url='https://spclient.wg.spotify.com/signup/public/v2/account/create', headers=headers, json=payload)

                if r.status_code == 200 and 'success' in r.text:
                    
                    Console.created += 1
                    
                    if self.verification_settings['Verify_Mail'] == 'y':
                        if '@gmail.com' in mail:
                            self.createAccount(session, username, mail, password, client_token, None, emailnator, r.json()['success'])
                        else:
                            self.createAccount(session, username, mail, password, client_token, inbox, None, r.json()['success'])

                    else:
                        self.createAccount(session, username, mail, password, client_token, None, None, r.json()['success'])

                elif 'challenge' in r.text:
                    self.console.printi('Account not created. Bypassing captcha challenge...')
                    session_id = r.json()['challenge']['session_id']

                    if self.settings['Use_Proxy'] == 'y':
                        account_data = self.bypassChallenge(session, client_token, client_id, session_id, proxy)
                    else:
                        account_data = self.bypassChallenge(session, client_token, client_id, session_id)
                        
                        
                    if account_data is not None:
                        Console.created += 1
                        if self.verification_settings['Verify_Mail'] == 'y':
                            self.createAccount(session, username, mail, password, client_token, inbox, emailnator, account_data)
                        else:
                            self.createAccount(session, username, mail, password, client_token, None, None, account_data)

                elif 'VPN' in r.text:
                    try:
                        self.console.printe(f'Account not created. Bad proxy: {proxy}')
                        if self.settings['Remove_Bad_Proxies'] == 'y':
                            self.proxies.remove(proxy)
                    except UnboundLocalError:
                        self.console.printe(f'Account not created. Please don\'t use the tool with VPN. If you are not using a VPN, you are in a location that cannot use this app. Please run the program using a proxy.')
                
                elif 'invalid_country' in r.text:
                    try:
                        self.console.printe(f'Account not created. Proxy\'s location is not suitable for Spotify: {proxy}')
                        if self.settings['Remove_Bad_Proxies'] == 'y':
                            self.proxies.remove(proxy)
                    except UnboundLocalError:
                        self.console.printe(f'Account not created. Please don\'t use the tool with VPN. If you are not using a VPN, you are in a location that cannot use this app. Please run the program using a proxy.')
                              
                
                else:
                    self.console.printe('Account not created.')
                    if self.settings['Debug_Mode'] == 'y':
                        self.debugMode(r.text, r.status_code)

            except Exception as e:
                self.console.printe(f'{str(e).capitalize()}. Retrying...')
                continue

        self.console.printtc(threading.current_thread().name.rstrip(' (main)').replace('-', ' ') + ' is closed.')

    def start(self):
        threading.Thread(target=self.tools.titleChanger, args=[self.target_settings['Use_Target'], self.target_settings['Target_To']], name='Title Changer').start()
        while threading.active_count() < self.settings['Threads'] + 2:
            threading.Thread(target=self.main).start()


if __name__ == '__main__':
    if checkVersion():
        gen = Gen()
        gen.start()
    else:
        print('Found some updates on the project! Download the latest version from https://github.com/seadhy/Spotify-Account-Creator to use the tool!')
