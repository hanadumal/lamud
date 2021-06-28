import telegram


def send(buffer, sid, token):
    """
    :param buffer:
    :return:
    """
    bot = telegram.Bot(token=token)
    bot.send_message(chat_id=str(sid), text=buffer)