# thank you github.com/6accOnThe6locc

from random import randint, choice, choices

def getUsername() -> str:    
    nick = list()
    prefix = str()
    under_score = str()
    under_score2 = str()
    rnd_number = str()
    rnd_vowels = choices(('a', 'e', 'i', 'o', 'u', 'y'), k=randint(3, 5))
    rnd_consonant = choices(('b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'y', 'z'), k=randint(4, 6))
    
    nick = [f"{x}{y}" for x,y in list(zip(rnd_vowels, rnd_consonant))]
    if choice((True, False)):
        if choice((True, False)):
            under_score = "_"
            
        prefix = choice(('Mr','Ms','Sir','Doctor','Lord','Lady','Rabbi','General','Captain','Glide','Deedee','Dazzle','Daydream','Micro','Lion','Punch','Hawk','Sandy','Hound','Rusty','Tigress','Commando','Abbot','Invincible','SepuLtura','Detective','Vanguard', 'Storm', 'Soulfly', 'Marine', 'Saber', 'Parachute', '4Justice', 'StrongHold', 'Thunder', 'Discoverer', 'Explorer', 'Cardinal','Winner','Bee', 'Coach', 'Munchkin', 'Teddy', 'Scout',' Smarty', 'Dolly', 'Princess','Pumpkin', 'Sunshine', 'Tinkerbell', 'Bestie', 'Sugar', 'Juliet', 'Magician', 'Mule', 'Stretch', 'Missile', 'Alpha', 'Grace', 'Buck', 'King', 'Chief', 'Oldie', 'Poker', 'Bustier', 'Adonis', 'Squirt', 'Ace', 'Mortal', 'Speedy', 'Bug', 'Senior', 'Bear', 'Rifle', 'Insomnia', 'JustWatch', 'Thanatos', 'Creature', 'Miracle', 'SuperHero', 'WhoAmI', 'Handyman','TheTalent','Boss','Meow','Ms.Congeniality', 'Rapunzel', 'Dolly', 'Sunshine', 'Eirene', 'Drum'))
        
    if choice((True, False)):
        if choice((True, False)):
            under_score2 = "_"
        rnd_number = f'{under_score2}{randint(1, 99)}'
        
    nick = prefix + under_score + "".join(nick).capitalize() + rnd_number
    return nick
