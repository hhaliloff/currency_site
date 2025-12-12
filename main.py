import urllib
from http.server import HTTPServer, BaseHTTPRequestHandler
from types import NoneType
import requests
from models import user_model, currency_model, app_model, subscription_model
from currency_api.currency_api import get_currencies
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
from urllib.parse import urlparse, parse_qs
from controllers.DatabaseController import DatabaseController
from controllers.TemplateController import (
    render_currencies,
    render_index,
    render_about_us,
    render_registration,
    render_registration_successfull,
    render_registration_fail,
    render_login,
    get_login_passwords,
    render_login_successfull,
    render_login_fail,
    db,
    get_logins,
    get_users, render_currencies_with_final
)

from controllers.TemplateController import db, get_logins
from http.cookies import SimpleCookie
import secrets

sessions = {}


"""
test_currency = currency_model.currency("840", "USD", "Доллар США", 74.36, 1)
test_subscription = subscription_model.subscription("test_user", "USD")
test_user = user_model.user("test_user", "Тестовый Пользователь", "password123")
"""


class MyHandler(BaseHTTPRequestHandler):
    def get_current_user(self):
        cookie_header = self.headers.get("Cookie")
        if not cookie_header:
            return None

        cookie = SimpleCookie(cookie_header)
        if "session_id" not in cookie:
            return None

        session_id = cookie["session_id"].value
        return sessions.get(session_id)

    def do_POST(self):

        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)

        if parsed_path.path == '/registration':
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length).decode("utf-8")
            data = urllib.parse.parse_qs(data)
            user_name = data.get('name', [''])[0]
            user_login = data.get('login', [''])[0]
            user_password = data.get('password', [''])[0]
            print("Пользователь ввёл:", user_name, user_login, user_password)
            if user_name == '' or user_login == '' or user_password == '':
                self.send_response(302)
                self.send_header('Location', '/registration_fail')
                self.end_headers()
            elif user_login in get_logins():
                self.send_response(302)
                self.send_header('Location', '/registration_fail')
                self.end_headers()
            else:
                db.create_user(user_login, user_name, user_password)
                self.send_response(302)
                self.send_header('Location', '/registration_successfull')
                self.end_headers()

        if parsed_path.path == '/login':
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length).decode("utf-8")
            data = urllib.parse.parse_qs(data)
            user_login = data.get('login', [''])[0]
            user_password = data.get('password', [''])[0]
            print("Пользователь ввёл:", user_login, user_password)
            logins = get_logins()
            login_password = get_login_passwords()
            if user_login in logins and login_password[user_login] == user_password:
                session_id = secrets.token_hex(16)

                # TODO: достать имя пользователя из БД
                # Пример: допустим, у тебя есть метод db.get_user_by_login(login)
                user_row = db.get_user_by_login(user_login)  # сам реализуешь в DatabaseController
                # допустим, структура user_row: (id, login, name, password_hash)

                user_data = {
                    "id": user_row[0],
                    "login": user_row[1],
                    "name": user_row[2],
                    # "password": user_password   # так делать не нужно, но технически можно
                }

                sessions[session_id] = user_data

                self.send_response(302)
                self.send_header('Location', '/login_successfull')
                self.send_header('Set-Cookie', f'session_id={session_id}; HttpOnly; Path=/')
                self.end_headers()
            else:
                self.send_response(302)
                self.send_header('Location', '/login_fail')
                self.end_headers()

        if parsed_path.path == '/add_favorites':
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length).decode("utf-8")
            data = urllib.parse.parse_qs(data)
            valute = data.get('currency_name', [''])[0]
            user = self.get_current_user()

            if user:
                db.create_subscription(user["login"], valute)

            self.send_response(302)
            self.send_header("Location", "/currencies")
            self.end_headers()

        if parsed_path.path == '/count':
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length).decode("utf-8")
            params = urllib.parse.parse_qs(data)
            print(params)
            rubles = float(params["rubles_value"][0])
            currency_value = float(params["currency_value"][0])
            currency_nominal = float(params["currency_nominal"][0])
            char_code = params["currency_char_code"][0]

            result = rubles / currency_value * currency_nominal

            final_values = [rubles, result, char_code]

            user = self.get_current_user()
            if user is not None:
                user["final_values"] = final_values

            self.send_response(302)
            self.send_header('Location', '/currencies_with_final')
            self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        current_user = self.get_current_user()

        if parsed_path.path == '/':
            html = render_index(user=current_user)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))

        if parsed_path.path == '/currencies':
            news = (requests.get("https://www.rbc.ru/quote/tag/currency").text).split(">")
            clas = news.index('\n                <span class="g-inline-text-badges__text"')
            news = news[clas + 1]
            news = news[:-6].lstrip()
            if current_user is not None:
                subs = db.subs_by_login(current_user["login"])
                subs = set(subs)
                print(subs)
                html = render_currencies(user=current_user, subs=subs, news=news)
            else:
                html = render_currencies(user=current_user, news=news)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))

        if parsed_path.path == '/currencies_with_final':
            news = (requests.get("https://www.rbc.ru/quote/tag/currency").text).split(">")
            clas = news.index('\n                <span class="g-inline-text-badges__text"')
            news = news[clas + 1]
            news = news[:-6].lstrip()
            final_values = None
            if current_user is not None:
                subs = db.subs_by_login(current_user["login"])
                subs = set(subs)
                print(subs)
                final_values = current_user.get("final_values")
                print(final_values)
                html = render_currencies_with_final(user=current_user, subs=subs, final_values=final_values, news=news)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))

        if parsed_path.path == '/aboutus':
            html = render_about_us(user=current_user)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))

        if parsed_path.path == '/registration':
            html = render_registration(user=current_user)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))

        if parsed_path.path == '/registration_successfull':
            html = render_registration_successfull(user=current_user)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))

        if parsed_path.path == '/registration_fail':
            html = render_registration_fail(user=current_user)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))

        if parsed_path.path == '/login':
            html = render_login(user=current_user)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))

        if parsed_path.path == '/login_successfull':
            html = render_login_successfull(user=current_user)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))

        if parsed_path.path == '/login_fail':
            html = render_login_fail(user=current_user)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))



if __name__ == "__main__":
    httpd = HTTPServer(("localhost", 8000), MyHandler)
    print("Server is running on http://localhost:8000")
    httpd.serve_forever()

