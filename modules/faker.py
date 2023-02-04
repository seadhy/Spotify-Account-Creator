import httpx
from string import ascii_letters, digits, ascii_lowercase
from random import choices, choice, randint
from os import listdir
from modules.username_creator import getUsername


class Faker:
    def __init__(self) -> None:
        self.usernames = open('data/usernames.txt', 'r', encoding='utf-8').read().splitlines()
        self.avatars = listdir('data/avatars')

    def getPassword(self, len_pass: int) -> str:
        return "".join(choices(ascii_letters + digits, k=len_pass))

    def getMail(self, len_email: int) -> str:
        return "".join(choices(ascii_lowercase + digits, k=len_email)) + choice(['@gmail.com', '@yahoo.com', '@outlook.com', '@hotmail.com', '@protonmail.com'])

    def getUsername(self, create_ai: str) -> str:
        if create_ai == 'n': return choice(self.usernames)
        return getUsername()

    def getAvatar(self, with_ai: str) -> bytes:
        if with_ai.lower() == 'y':
            api = 'https://picsum.photos/512/512'
            r = httpx.get(url=api)
            img_url = (r.headers['location'])

            response = httpx.get(url=img_url)

            if response.status_code == 200:
                with open('data/avatars/temp_image.png', 'wb') as f:
                    f.write(response.content)
                with open('data/avatars/temp_image.png', 'rb') as f:
                    return f.read()
        image = open('data/avatars/' + choice(self.avatars), 'rb').read()
        return image

    def getBirthday(self) -> str:
        day = str(randint(1, 28))
        month = str(randint(1, 12))

        if int(month) < 10: month = "0" + month
        if int(day) < 10: day = "0" + day

        birthday = "-".join([str(randint(1910, 2004)), month, day])
        return birthday
