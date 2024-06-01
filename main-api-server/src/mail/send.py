from src.mail.smtp import SMTPClient


async def send_to_resumer(data: dict):
    message = f"Для дальнейшего изучения резюме нам не хватает следующих данных: "
    if data['experience'] == '' or data['experience'] is None:
        message += "опыт работы, "
    if data['degree'] == '' or data['degree']:
        message += "профессиональный уровень, "
    if data['position'] == '' or data['position']:
        message += "должность"
    smtp = SMTPClient()
    smtp.send("mhlvvln_test_pks@rambler.ru",
              "ivan.sygin@yandex.ru",
              "Резюме на трудоустройство",
              message)
