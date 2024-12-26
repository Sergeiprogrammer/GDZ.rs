import telebot

# Токен твоего бота от BotFather
TOKEN = "6898197210:AAFMFGS7W9-yWSqYj14enTTswoWZRkSvjz8"
bot = telebot.TeleBot(TOKEN)

CHAT_ID = "-1002439408643"  # Укажите правильный chat_id группы

class Telegramm_sent:
    @staticmethod
    def send_text_to_me(message):
        try:
            bot.send_message(CHAT_ID, message)
            print("Сообщение отправлено!")
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Ошибка при отправке сообщения: {e}")
        except Exception as ex:
            print(f"Другая ошибка: {ex}")

    @staticmethod
    def send_file_as_document(file_path, file_name=None):
        try:
            with open(file_path, 'rb') as file:
                bot.send_document(CHAT_ID, file, caption=file_name or "Файл")
                print("Файл отправлен!")
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Ошибка при отправке файла: {e}")
        except Exception as ex:
            print(f"Другая ошибка: {ex}")

    @staticmethod
    def send_admin_submission(topic, title, additional_info, admin_name):
        try:
            message = (
                f"Администратор {admin_name} добавил новую тему:\n\n"
                f"Тема: {topic}\n"
                f"Заголовок: {title}\n"
                f"Дополнительная информация: {additional_info}"
            )
            bot.send_message(CHAT_ID, message)
            print("Информация об администраторе отправлена!")
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Ошибка при отправке сообщения: {e}")
        except Exception as ex:
            print(f"Другая ошибка: {ex}")
