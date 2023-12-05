import secrets
import string


def proccess_start(): # Генерация случайных символов
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(10, 15))
    return password
