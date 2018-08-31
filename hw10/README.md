### Домашняя работа 10 - Ansible+Django

1. Правила хорошего тона - нужно создать виртуальное окружение для предотвращения конфликта зависимостей
```
cd /opt
mkdir django
virtualenv django
cd django
. bin/activate
```

2. После этого можно скачать сюда репозиторий:
```
git clone http://bitbucket.fintech-admin.m1.tinkoff.cloud/scm/pub/addressbook.gitgit
```
Смотрим в settings.py, чтобы определить нужную версию django, видим 2.0.7
```
pip install django~=2.0.7
```

2. Создаем в Postgresql пользователя django, БД addressbook
```
pip install psycopg2
psql -U postgres -p 6789
CREATE USER django;
ALTER USER django WITH PASSWORD 'django';
CREATE DATABASE addressbook;
GRANT ALL PRIVILEGES ON DATABASE addressbook TO django;
```
Также добавляем в pg_hba.conf (в т.ч. IPv6, иначе - ошибка)
```
host    addressbook     django          127.0.0.1/32            md5
host    addressbook     django          0.0.0.0/0               md5
host    addressbook     django          ::1/128                 md5
```

И редактируем settings.py, учитывая, что Postgres слушает на порту 6789:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME':  'addressbook',
        'USER':  'django',
        'PASSWORD': 'django',
        'HOST': 'localhost',
        'PORT': '6789',
    }
}
```

3. Выполняем миграции:
```
python manage.py migrate
```

4. Создадим суперпользователя (manage.py createsuperuser), побалуемся и увидим, что при logout возникает ошибка "NoReverseMatch at /accounts/logout/"
> Данная ошибка связана с тем, что шаблон logout ищется сначала в директориях стандартных приложений (т.к. порядок поиска соответствует порядку описания приложений в INSTALLED_APPS). Поэтому и находится <venv_root>/lib/python3.6/site-packages/django/contrib/admin/templates/registration/logged_out.html. Но в нем есть отсылка к admin:index, а мы не подключали в URL-ы ничего от пространства имен admin. Поэтому для корректной работы нужно поменять порядок приложений в settings.py:
> Обновленное приложение - на гитхабе
```
INSTALLED_APPS = [
    'addressbook',
    'contacts',
    'django.contrib.admin',
    'django.contrib.auth',
    <...>
```

5. Настраиваем systemd для запуска django при старте системы, добавляем его в webserver.target, но сначала создаем пользователя django
```
useradd django
cd /opt
chown -R django:django django
```

Venv уже "встроен" в python, лежащий в <venv_dir>/bin, дополнительной активации производить не требуется  
Используем порт 8000, т.к. потом нужно будет производить upstream из nginx. Порт 8080 оставим для uwsgi-приложений (тоже upstream из nginx)

Файл django.service (на гитахабе)
```
[Unit]
Description=Django web server
After=network-online.target

[Service]
User=django
Restart=on-failure
WorkingDirectory=/opt/django/
ExecStart=/opt/django/bin/python /opt/django/addressbook/manage.py runserver 0.0.0.0:8800

[Install]
WantedBy=webserver.target
```

6. Репозиторий с ролями для nginx и postgresql - на гитхабе.
http://bitbucket.fintech-admin.m1.tinkoff.cloud/scm/usr15/ansible.git  
Примечания: 
> Разворачивает только nginx, предполагает, что django приложение уже установлено  
> WantedBy=webserver.target - оставлено в конфигурации юнита systemd (потому что теоретически мы могли бы сделать webserver.targer, но нет задания развертывания uwsgi)  
> Чтобы как можно меньше использовать trust-авторизацию, для изменения pg_hba.conf используется sed. После этого для подключения к postgres
> .vault_pass.txt - вне репозитория (т.к. в .gitignore)
