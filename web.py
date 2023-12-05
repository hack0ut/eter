import configparser
from redis import Redis
from modules import account_manage, generate_code, notification, telegram
from flask import Flask, render_template, session, redirect, request

app = Flask(__name__)
redis = Redis(decode_responses=True) # Инициализация БД
config = configparser.ConfigParser() # Парсер конфиг файла
config.read("web.ini")


@app.route("/") # Главная страница
def index():
    uid = 0
    name = None
    password = None
    if "password" in session: # Если пароль есть в сессии браузера
        name = session['name']
        uid = session['uid']
        password = session['password']
    if redis.get("id") is None:
        uids = 0 # Если в БД нет зарегистрированных
    else:
        uids = redis.get("id")
    return render_template("index.html", uid=uid, name=name, uids=uids, password=password)
    # Возвращаем страницу со всеми нужными данными


@app.route("/feedback/sent", methods=['POST']) # Отправка отзыва
def feedback_sent():
    if "password" in session: # Если пользователь зарегистрирован
        name = session['name']
        uid = session['uid']
        email = session['email']
        rate = request.values['rate']
        fbk = request.values['feedback']
        telegram.send_message(f"Новый отзыв!\n\n👤 {name}\n📪 {email}\n🆔 {uid}\n💬 {fbk}\n🌟 {rate}\n\n#feedback #отзыв")
        return notification.send_message('Отзыв отправлен!', '/')
    else:
        return notification.send_message('Вы не авторизованы!', '/')


@app.route("/feedback")
def feedback():
    return render_template("feedback.html") # Отрисовка страницы с feedback'ом


@app.route("/contacts")
def contacts():
    return render_template("contacts.html") # Отрисовка страницы с контактами


@app.route('/FAQ')
def fast_answer_question():
    return render_template("faq.html") # Отрисовка страницы с Fast Answer Question


@app.route('/new_quest/sent', methods=['POST']) # Отправка вопроса о сайте
def send_question():
    if "password" in session:
        name = session['name']
        uid = session['uid']
        email = session['email']
        text = request.values['text']
        telegram.send_message(f"Новый вопрос!\n\n👤 {name}\n📪 {email}\n🆔 {uid}\n💬 {text}\n\n#question #вопрос")
        return notification.send_message('Отправлено!', '/')
    else:
        return notification.send_message('Вы не авторизованы!', '/FAQ')


@app.route('/new_question') # Отрисовка формы с заданием нового вопроса
def question():
    if "password" in session:
        return render_template("new_question.html")
    else:
        return notification.send_message('Вы не авторизованы!', '/FAQ')


@app.route("/get_key")
def give_access_key(): # Выдача ключа для удаления аккаунта
    if "password" in session:
        code = generate_code.proccess_start()
        redis.set(f"email:{session['email']}:access_key", code)
        return f'Ваш код - {code}. <br><br><a href="/">На главную</a>' # Немного костылей
    else:
        return notification.send_message("Вы не авторизованы", "/")


@app.route("/deactivate")
def deactivate_profile(): # Страница с деактивацией(удалением) профиля
    if "password" in session:
        return render_template("deactivate_profile.html")
    else:
        return notification.send_message("Вы не авторизованы", "/")


@app.route("/deactivate/start", methods=['POST']) # Процесс удаления аккаунта
def deactivate_profile_start():
    if "password" in session:
        if request.values['access_key'] == redis.get(f"email:{session['email']}:access_key"):
            account_manage.delete_account(session['email'])
            return notification.send_message("Аккаунт был удален. Надеюсь, еще встретимся :)", "/")
        else:
            return notification.send_message("Неверный код доступа!", "/deactivate")
    else:
        return notification.send_message("Вы не авторизованы", "/")


@app.route('/profile') # Отрисовка страницы с профилем
def profile():
    if "password" in session:
        email, name, bday, password, gender, uid, age = account_manage.get_info(False)
        return render_template("profile.html", email=email, name=name, bday=bday, password=password,
                               gender=gender, uid=uid, age=age)
    else:
        return notification.send_message("Вы не авторизованы!", "/")


@app.route('/logout') # Выход из аккаунта
def logout():
    if "password" in session:
        account_manage.logout()
        return notification.send_message("Вы успешно вышли из аккаунта!", "/")
    else:
        return redirect("/")


@app.route('/login') # Авторизация
def login():
    if "password" in session:
        return redirect("/")
    else:
        return render_template("login.html")


@app.route('/fastlogin', methods=['POST']) # Процесс авторизации
def login_redis():
    email = request.values['email']
    password = request.values['password']
    if redis.get(f"email:{email}") == "registered":
        if redis.get(f"email:{email}:password") == password:
            account_manage.authorize_account(email, password)
            return notification.send_message(f"Вы успешно авторизовались под аккаунтом {email}.", "/")
        else:
            return notification.send_message("Неверный пароль!", "/login")
    else:
        return notification.send_message("Аккаунт не найден!", "/login")


@app.route('/register') # Регистрация
def registration():
    if "password" in session:
        return redirect("/")
    else:
        return render_template("register.html")


@app.route('/fastreg', methods=['POST']) # Процесс регистрации
def register_redis():
    email = request.values['email']
    name = request.values['name']
    bday = request.values['bday']
    gender = request.values['gender']
    password = request.values['password']
    confirm_password = request.values['confirm_password']
    uid = redis.incr("id")
    uids = redis.get("id")
    if redis.get(f"email:{email}") == "registered":
        return notification.send_message("Данный E-Mail уже зарегистрирован!", "/register")
    else:
        if password == confirm_password:
            account_manage.create_email_account(email, name, bday, password, gender, uid)
            return notification.send_message(f"Спасибо за регистрацию! Вы уже {uids} в системе!", "/")
        else:
            return notification.send_message("Введенные пароли не совпадают", "/register")


if __name__ == '__main__':
    telegram.web_started(beta=False) # Инициализация телеграм-бота
    app.secret_key = generate_code.proccess_start() # Генерация "секретного ключа"
    context = ('keys/cert.crt', 'keys/key.key') # Сертификаты
    app.run(config["webserver"]["web_domain"], int(config["webserver"]["web_port"]), ssl_context=context) # Запуск сайта
