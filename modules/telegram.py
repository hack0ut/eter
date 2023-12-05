import telebot

bot = telebot.TeleBot('Токен вашего бота из BotFather')
trusted_tgid = 1228405574


def web_started(beta):
    markup = telebot.types.InlineKeyboardMarkup()
    site1 = telebot.types.InlineKeyboardButton(text='🔗 Перейти на сайт 🔗', url='http://eternity-empire.ru/')
    markup.add(site1)
    if beta:
        site2 = telebot.types.InlineKeyboardButton(text='💻 Локальный сайт', url='http://172.26.106.221/')
        markup.add(site2)
    bot.send_message(trusted_tgid, "ℹ️ Серверная часть сайта была запущена!", reply_markup=markup)


def new_user(email, name, bday, gender, uid):
    text = f"Зарегистрирован новый пользователь!\n\n📪 {email}\n👤 {name}\n📅 {bday}\n🚹 {gender}\n🆔 {uid}"
    bot.send_message(trusted_tgid, text + "\n\n#new_user #новый_пользователь")


def send_message(text):
    bot.send_message(trusted_tgid, text)
