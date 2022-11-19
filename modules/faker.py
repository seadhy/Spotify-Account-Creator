from string import ascii_letters, digits, ascii_lowercase
from random import choices, choice, randint
from glob import glob
from modules.username_creator import getUsername


class Faker:
    def __init__(self) -> None:
        self.usernames = open('data/usernames.txt','r',encoding='utf-8').read().splitlines()
    
    def getPassword(self, len_pass: int) -> str:
        return "".join(choices(ascii_letters+digits, k=len_pass))
    
    def getMail(self, len_email: int) -> str:
        return "".join(choices(ascii_lowercase + digits, k=len_email)) + choice(['@gmail.com','@yahoo.com','@outlook.com','@hotmail.com','@protonmail.com'])
    
    def getUsername(self, create_ai: str) -> str:
        if create_ai == 'n': return choice(self.usernames)
        return getUsername()
    
    def getAvatar(self) -> bytes:
        file_path_type = ["data/avatars/*.jpg"]  # can change file extansion png, jpeg etc.

        images = glob(choice(file_path_type))
        random_image = choice(images)
        image_path = str(random_image).replace('\\','/')
        image = open(image_path, 'rb').read()
        return image

    def getBirthday(self) -> tuple:
        day = str(randint(1,28))
        month = str(randint(1,12))
        
        if int(month) < 10: month = "0" + month
        if int(day) < 10: day = "0" + day
        
        birthday = "-".join([str(randint(1910, 2004)), month, day])
        return birthday