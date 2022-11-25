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

    def getAvatar(self) -> bytes:
        image = open('data/avatars/' + choice(self.avatars), 'rb').read()
        return image

    def getBirthday(self) -> str:
        day = str(randint(1, 28))
        month = str(randint(1, 12))

        if int(month) < 10: month = "0" + month
        if int(day) < 10: day = "0" + day

        birthday = "-".join([str(randint(1910, 2004)), month, day])
        return birthday
