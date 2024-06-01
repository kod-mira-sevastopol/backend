from src.mail.data import Data


class SenderClient(Data):
    def __init__(self):
        super().__init__()

    def send(self, from_user: str, to_user: str, subject: str, text: str):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

