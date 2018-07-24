#!/usr/bin/python

from cgi import parse_qs

# Любое wsgi-приложение реализовано как функция
# env - переменные окружения: среды + WSGI-специфичные
# start_response - обработчик запроса, его нужно вызвать
# Функция должна вернуть итерируемый объект (который будет итерироваться при загрузках страницы)
def application(env, start_response):
    start_response('200 OK', [('Content-Type','text/plain')]) # Первый аргумент - код ответа, второй - заголовки ответа

    wsgi_content = env["wsgi.input"].read(0) # Читаем тело запроса
    request_uri_content = env["REQUEST_URI"] # Читаем URI загружаемой страницы
    request_method_content = env["REQUEST_METHOD"] # Получаем метод загрузки
    d = parse_qs(wsgi_content) # Возвращает dict с параметрами запроса
    return ["Method: " + request_method_content + "\n" +
        "Get content: " + request_uri_content + "\n" +
        "Post content: " + wsgi_content + "\n"] #Возвращам страницу
