from os import getenv

from dotenv import load_dotenv


class Data:
    def __init__(self):
        load_dotenv()
        self.username = getenv("mail")
        self.password = getenv("password")