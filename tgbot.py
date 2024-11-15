import telebot

# Токен твоего бота от BotFather
TOKEN = "6986591700:AAF09IXA7OintoNq04QdnmQwoX3-LlaazZs"  # Твой токен
bot = telebot.TeleBot(TOKEN)

class Telegramm_sent:
    @staticmethod
    def send_text_to_me(message):
        chat_id = "5131136267"  # Замени на свой реальный chat_id
        bot.send_message(chat_id, message)

    @staticmethod
    def send_file_as_document(file_path, file_name=None):
        chat_id = "5131136267"  # Замени на свой реальный chat_id
        with open(file_path, 'rb') as file:
            bot.send_document(chat_id, file, caption=file_name or "Файл")


