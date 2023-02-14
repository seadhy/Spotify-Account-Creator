import threading
from colorama import Fore
from threading import Lock, active_count
from time import sleep, perf_counter
from datetime import datetime
from ctypes import windll
from pystyle import Center, Colors, Colorate

lock = Lock()


class Console:
    created = 0

    @staticmethod
    def printsc(content: str):
        lock.acquire()
        print(
            f"{Fore.LIGHTBLACK_EX}[{Fore.LIGHTWHITE_EX}{datetime.strftime(datetime.now(), '%X').replace(':', f'{Fore.LIGHTBLACK_EX}:{Fore.LIGHTWHITE_EX}')}{Fore.LIGHTBLACK_EX}] {Fore.LIGHTBLACK_EX}[{Fore.LIGHTGREEN_EX}Account Created{Fore.LIGHTBLACK_EX}]{Fore.LIGHTWHITE_EX} > {content}")
        lock.release()

    @staticmethod
    def printe(content: str):
        lock.acquire()
        print(
            f"{Fore.LIGHTBLACK_EX}[{Fore.LIGHTWHITE_EX}{datetime.strftime(datetime.now(), '%X').replace(':', f'{Fore.LIGHTBLACK_EX}:{Fore.LIGHTWHITE_EX}')}{Fore.LIGHTBLACK_EX}] {Fore.LIGHTBLACK_EX}[{Fore.LIGHTRED_EX}Error Occurred{Fore.LIGHTBLACK_EX}]{Fore.LIGHTWHITE_EX} > {content}")
        lock.release()

    @staticmethod
    def printi(content: str):
        lock.acquire()
        print(
            f"{Fore.LIGHTBLACK_EX}[{Fore.LIGHTWHITE_EX}{datetime.strftime(datetime.now(), '%X').replace(':', f'{Fore.LIGHTBLACK_EX}:{Fore.LIGHTWHITE_EX}')}{Fore.LIGHTBLACK_EX}] {Fore.LIGHTBLACK_EX}[{Fore.LIGHTYELLOW_EX}Info{Fore.LIGHTBLACK_EX}]{Fore.LIGHTWHITE_EX} > {content}")
        lock.release()

    @staticmethod
    def printm(content: str):
        lock.acquire()
        print(
            f"{Fore.LIGHTBLACK_EX}[{Fore.LIGHTWHITE_EX}{datetime.strftime(datetime.now(), '%X').replace(':', f'{Fore.LIGHTBLACK_EX}:{Fore.LIGHTWHITE_EX}')}{Fore.LIGHTBLACK_EX}] {Fore.LIGHTBLACK_EX}[{Fore.LIGHTBLUE_EX}Mail Verified{Fore.LIGHTBLACK_EX}]{Fore.LIGHTWHITE_EX} > {content}")
        lock.release()

    @staticmethod
    def printhc(content: str):
        lock.acquire()
        print(
            f"{Fore.LIGHTBLACK_EX}[{Fore.LIGHTWHITE_EX}{datetime.strftime(datetime.now(), '%X').replace(':', f'{Fore.LIGHTBLACK_EX}:{Fore.LIGHTWHITE_EX}')}{Fore.LIGHTBLACK_EX}] {Fore.LIGHTBLACK_EX}[{Fore.LIGHTMAGENTA_EX}Humanization Completed{Fore.LIGHTBLACK_EX}]{Fore.LIGHTWHITE_EX} > {content}")
        lock.release()

    @staticmethod
    def printtc(content: str):
        lock.acquire()
        print(
            f"{Fore.LIGHTBLACK_EX}[{Fore.LIGHTWHITE_EX}{datetime.strftime(datetime.now(), '%X').replace(':', f'{Fore.LIGHTBLACK_EX}:{Fore.LIGHTWHITE_EX}')}{Fore.LIGHTBLACK_EX}] {Fore.LIGHTBLACK_EX}[{Fore.LIGHTCYAN_EX}Thread Closed{Fore.LIGHTBLACK_EX}]{Fore.LIGHTWHITE_EX} > {content}")
        lock.release()


class Tools:

    @staticmethod
    def titleChanger(use_target: str, target_to: int):
        windll.kernel32.SetConsoleTitleW('Initializing...')

        starting_time = perf_counter()
        while True:
            sleep(0.1)
            created_min = round(Console.created / ((perf_counter() - starting_time) / 60), 1)
            if use_target == 'y':
                remaining = target_to - Console.created
                if remaining > 0:
                    windll.kernel32.SetConsoleTitleW(f"Seasmash Spotify Creator  |  Threads: {active_count() - 2}  |  Created: {Console.created}  |  Speed: {created_min}/m  |  Remaining: {remaining}  |  Elapsed: {round(perf_counter() - starting_time, 1)}s  |  Made by github.com/seadhy")
                else:
                    windll.kernel32.SetConsoleTitleW(f"Seasmash Spotify Creator  |  Threads: {active_count() - 2}  |  Created: {Console.created}  |  Speed: {created_min}/m  |  Remaining: {remaining}  |  Elapsed: {round(perf_counter() - starting_time, 1)}s  |  Made by github.com/seadhy")
                    sleep(5)
                    Console.printtc(threading.current_thread().name + " is closed. The program will close itself in 3 seconds...")
                    sleep(3)
                    exit()
            else:
                windll.kernel32.SetConsoleTitleW(f"Seasmash Spotify Creator  |  Threads: {active_count() - 2}  |  Created: {Console.created}  |  Speed: {created_min}/m  |  Elapsed: {round(perf_counter() - starting_time, 1)}s  |  Made by github.com/seadhy")

    @staticmethod
    def printLogo():
        print(Colorate.Vertical(Colors.purple_to_blue, Center.XCenter("""
           ▄████████    ▄████████    ▄████████    ▄████████   ▄▄▄▄███▄▄▄▄      ▄████████    ▄████████    ▄█    █▄    
          ███    ███   ███    ███   ███    ███   ███    ███ ▄██▀▀▀███▀▀▀██▄   ███    ███   ███    ███   ███    ███   
          ███    █▀    ███    █▀    ███    ███   ███    █▀  ███   ███   ███   ███    ███   ███    █▀    ███    ███   
          ███         ▄███▄▄▄       ███    ███   ███        ███   ███   ███   ███    ███   ███         ▄███▄▄▄▄███▄▄ 
        ▀███████████ ▀▀███▀▀▀     ▀███████████ ▀███████████ ███   ███   ███ ▀███████████ ▀███████████ ▀▀███▀▀▀▀███▀  
                 ███   ███    █▄    ███    ███          ███ ███   ███   ███   ███    ███          ███   ███    ███   
           ▄█    ███   ███    ███   ███    ███    ▄█    ███ ███   ███   ███   ███    ███    ▄█    ███   ███    ███   
         ▄████████▀    ██████████   ███    █▀   ▄████████▀   ▀█   ███   █▀    ███    █▀   ▄████████▀    ███    █▀   
                      ⌜――――――――――――――――――――――――――――――――――――――――――――――――――――⌝
                      ┇      [Discord] https://discord.gg/6hP3mHKSqf       ┇
                      ┇      [Github]  https://github.com/seadhy           ┇
                      ⌞――――――――――――――――――――――――――――――――――――――――――――――――――――⌟
                      
                      """)))
