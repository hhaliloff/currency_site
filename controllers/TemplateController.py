from jinja2 import Environment, select_autoescape, FileSystemLoader
from controllers.DatabaseController import DatabaseController
from currency_api.currency_api import get_currencies
from models import app_model

actual_app = app_model.app("StuxNet", "0.2 Beta", "Чингиз Халилов")

env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape()
)

db = DatabaseController()


def get_logins():
    logins = []
    all_logins = db.read_user()
    for login in all_logins:
        logins.append(login[1])
    print(logins)
    return logins


def get_login_passwords():
    login_passwords = {}
    all_logins_passwords = db.read_user()
    for login_password in all_logins_passwords:
        login_passwords[login_password[1]] = login_password[3]
    print(login_passwords)
    return login_passwords

def get_users():
    users = []
    all_users = db.read_user()
    for user in all_users:
        users.append(user)
    print(users)
    return users

# если надо один раз загрузить валюты из API в БД
for currency in get_currencies():
    num_code = currency[0]
    char_code = currency[1]
    name = currency[2]
    value = currency[3]
    nominal = currency[4]
    db.create_currency(num_code, char_code, name, value, nominal)


def render_index(user=None):
    template = env.get_template('index.html')
    return template.render(actual_app=actual_app, user=user)


def render_currencies(user=None, subs=None, news=None):
    currencies = db.read_currency()
    template = env.get_template('currencies.html')
    return template.render(currencies=currencies, user=user, subs=subs, news=news)


def render_about_us(user=None):
    template = env.get_template('about_us.html')
    return template.render(actual_app=actual_app, user=user)


def render_registration(user=None):
    template = env.get_template('registration.html')
    return template.render(user=user)


def render_registration_successfull(user=None):
    template = env.get_template('registration_successfull.html')
    return template.render(user=user)


def render_registration_fail(user=None):
    template = env.get_template('registration_fail.html')
    return template.render(user=user)


def render_login(user=None):
    template = env.get_template('login.html')
    return template.render(user=user)


def render_login_successfull(user=None):
    template = env.get_template('login_successfull.html')
    return template.render(user=user)


def render_login_fail(user=None):
    template = env.get_template('login_fail.html')
    return template.render(user=user)

def render_currencies_with_final(user=None, subs=None, final_values=None, final_value=None, news=None):
    currencies = db.read_currency()
    template = env.get_template('currencies_with_final.html')
    return template.render(currencies=currencies, user=user, subs=subs, final_values=final_values, news=news)
