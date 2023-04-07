import requests
import json
import time
import re


class Emailnator:
    def __init__(self):
        self.base_url = "https://www.emailnator.com/"
        self.session = requests.Session()

    def getCookies(self):
        return self.session.get(self.base_url).cookies.get_dict()

    def generateMail(self, cookies, mail_type=None):
        data_cookie = json.loads(json.dumps(cookies))
        xsrf_token =  str(data_cookie['XSRF-TOKEN']).replace('%3D', "=")
        session_token = data_cookie['gmailnator_session']

        cookies  = {"XSRF-TOKEN": f"{xsrf_token}", "gmailnator_session": f"{session_token}"}
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json",
        "X-Xsrf-Token": f"{xsrf_token}",
        "Origin": "https://www.emailnator.com",
        "Referer": "https://www.emailnator.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Te": "trailers"
        }
        mail_json = {"email": ["dotGmail"] if mail_type == None else mail_type}
        mail = requests.post(self.base_url + "generate-email", headers=headers, cookies=cookies, json=mail_json).json()["email"][0]
        return mail

    def getVerificationLink(self, cookies, mail: str):
        mail_cookies = json.loads(json.dumps(cookies))
        xsrf_token = str(mail_cookies['XSRF-TOKEN']).replace('%3D', "=")
        session_token = mail_cookies['gmailnator_session']

        cookies = {"XSRF-TOKEN": f"{xsrf_token}", "gmailnator_session": f"{session_token}"}
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json",
        "X-Xsrf-Token": f"{xsrf_token}",
        "Origin": "https://www.emailnator.com",
        "Referer": "https://www.emailnator.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Te": "trailers"
        }

        mail_json = {"email": mail}

        while True:
            response = requests.post(self.base_url + "message-list", headers=headers, cookies=cookies, json=mail_json).json()
            messges_id = response['messageData']
            total_messeges = len(messges_id)

            for i in range(total_messeges):
                if len(str(messges_id[i]['messageID'])) > 12:
                    messges_id_base = messges_id[i]['messageID']
                    url_email = "https://www.emailnator.com/message-list"

                    json_mail = {
                        "email": f"{mail}",
                        "messageID": f"{messges_id_base}"}

                    message = requests.post(url_email, headers=headers, cookies=cookies, json=json_mail)
                    if "https://wl.spotify.com/" in message.text:
                        pattern = re.compile(r'https?://wl\.spotify\.com/ls/click\?.*')
                        verification_url = re.findall(pattern, message.text)[0].split('"')[0]
                        return verification_url
                        break
                    else:
                        continue
    
