import datetime
from modules import telegram
from redis import Redis
from flask import session

redis = Redis(decode_responses=True)


def create_email_account(email, name, bday, password, gender, uid): # Создание нового аккаунта
    redis.set(f"email:{email}:name", name) # Добавление имени в базу данных
    redis.set(f"email:{email}:bday", bday) # Добавление даты рождения в базу данных
    redis.set(f"email:{email}", "registered") # Добавление значения о регистрации
    redis.set(f"email:{email}:password", password) # Добавление пароля в базу данных
    redis.set(f"email:{email}:gender", gender) # Добавление гендера в базу данных
    redis.set(f"email:{email}:id", uid) # Добавление идентификационного номера пользователя в базу данных
    session['email'] = email # Добавление данных в браузер пользователя
    session['name'] = name
    session['bday'] = bday
    session['gender'] = gender
    session['password'] = password
    session['uid'] = uid
    telegram.new_user(session['email'], session['name'], session['bday'], session['gender'], session['uid'])
    # Отправка данных о том, что пользователь зарегистрирован в телеграм


def authorize_account(email: str, password: str): # Авторизация пользователя
    name = redis.get(f"email:{email}:name") # Получение и запись имени
    bday = redis.get(f"email:{email}:bday") # Получение и запись дня рождения
    gender = redis.get(f"email:{email}:gender") # Получение и запись гендера
    uid = redis.get(f"email:{email}:id") # Получение и запись идентификационного номера пользователя
    session['email'] = email
    session['name'] = name
    session['bday'] = bday
    session['gender'] = gender
    session['password'] = password
    session['uid'] = uid
    # Добавление всех значений в сессию браузера пользователя


def logout(): # Выход из аккаунта: Удаление значений о авторизации из браузера пользователя
    del session['email']
    del session['name']
    del session['bday']
    del session['gender']
    del session['password']
    del session['uid']


def get_info(visible): # Получение информации
    email = session['email']
    name = session['name']
    bday = session['bday']
    password = session['password']
    gender = session['gender']
    uid = session['uid']
    gender = gender.replace('female', 'Женский')
    gender = gender.replace('male', 'Мужской')
    try:
        today = datetime.datetime.today() # Получение нынешней даты
        nday = datetime.datetime.strptime(redis.get(f"email:{email}:bday"), '%Y-%m-%d') # Получение дня рождения пользователя
        age = (today - nday).days // 365 # Рассчет того, сколько пользователю лет
    except: # Если ошибка, то...
        age = "Ошибка 221, обратитесь в поддержку (она находится на странице 'контакты')"
    if not visible:
        i = len(password) # Замена всех символов пароля на "маркер списка"
        return email, name, bday, "•" * i, gender, uid, age
    else:
        return email, name, bday, password, gender, uid, age


def delete_account(email): # Удаление аккаунта из системы
    redis.delete(f"email:{email}:name")
    redis.delete(f"email:{email}:bday")
    redis.delete(f"email:{email}")
    redis.delete(f"email:{email}:password")
    redis.delete(f"email:{email}:gender")
    redis.delete(f"email:{email}:id")
    redis.delete(f"email:{email}:access_key")
    logout()
