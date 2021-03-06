import telegram


def send(buffer, sid=1254512302):
    """
    群ID： -545209393
    私聊ID：1254512302
    https://api.telegram.org/bot1646500683:AAF4Malw1jx0HjvhWQSQl7uJhdMJ3jVP1VE/getUpdates
    :param buffer:
    :return:
    """
    bot = telegram.Bot(token="1646500683:AAF4Malw1jx0HjvhWQSQl7uJhdMJ3jVP1VE")
    bot.send_message(chat_id=str(sid), text=buffer)