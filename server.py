from flask import Flask, redirect
import configparser

app = Flask(__name__)
config = configparser.ConfigParser()
config.read("web.ini")
domain = config["webserver"]["web_domain"]


@app.route("/")  # Создание главной страницы
def index():
    return redirect(f"https://{domain}")  # Редирект на тот же сайт, но с другим протоколом


if __name__ == "__main__":
    app.run(domain, 80)
