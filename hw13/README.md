### Домашняя работа 13 - docker

0. Останавливаем django: systemctl stop django.service

1. Устанавливаем docker
```
sudo yum install -y yum-utils device-mapper-persistent-data lvm2

# Берем репозиторий со стабильными сборками
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum -y install docker-ce
sudo systemctl start docker
sudo systemctl enable docker

# Проверем
sudo docker run hello-world
```

2. Устанавливаем docker compose
```
curl -L https://github.com/docker/compose/releases/download/1.22.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
cd /bin
ln /usr/local/bin/docker-compose docker-compose
```

3. Создаем контейнер для django
- Создаем директорию проекта, в ней Dockerfile (python 3.6.6, с 3.7 django не дружит, на всякий случай - очистка docker - "docker system prune --all --force --volumes"):
```
FROM python:3.6.6
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt

ADD . /code/
```

requirements.txt:
```
Django>=2.0.7
psycopg2
```

- Создаем docker-compose.yml:  
Данный файл определяет 2 сервиса: postgresql и django (образы сервисов мы сделаем позднее), определяет перенаправление портов и команду запуска django
```
version: '3'
services:
  db:
    image: postgres
  web:
    build: .
    command: python3 manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/code
    ports:
      - "8000:8000"
    depends_on:
      - db
```

- Начинаем проект  
Данная команда попытается выполнить django-admin.py startproject addressbook . в контейнере, используя конфигурацию сервиса web. Но, поскольку он еще не был создан, его образ будет создан в данной директории (build: .)
```
sudo docker-compose run web django-admin.py startproject addressbook .
```

- Далее перемещаемся в директорию /opt/django/addressbook, поскольку туда деплоится приложение из TeamCity (просто копируем туда файлы Dockerfile, requirements.txt и docker-compose.yml)  
Кроме того, исправляем settings.py под docker (меняем и в репозитории!):
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
    }
}
```

- Выполняем миграцию и запускаем django-приложение в контейнере:
```
docker-compose run web manage.py migrate
docker-compose up
```

- Добавляем контейнер в systemd
django.service unit (на гитхабе):
```
[Unit]
Description=Django service in docker
After=network.target docker.service

[Service]
Type=simple
WorkingDirectory=/opt/django/addressbook
ExecStart=/usr/local/bin/docker-compose -f /opt/django/addressbook/docker-compose.yml up
ExecStop=/usr/local/bin/docker-compose -f /opt/django/addressbook/docker-compose.yml down
Restart=always

[Install]
WantedBy=multi-user.target webserver.target
```