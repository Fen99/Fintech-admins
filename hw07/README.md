## Домашняя работа №7 - Prometheus

1. Скачать Prometheus, его exporters  
```
curl `curl https://github.com/prometheus/prometheus/releases/download/v2.3.2/prometheus-2.3.2.linux-amd64.tar.gz
```
<html><body>You are being <a href="...">redirected</a>.</body></html> - перенаправление => достанем url из него и скачаем (NodeExporter аналогично):  
```
curl `curl https://github.com/prometheus/prometheus/releases/download/v2.3.2/prometheus-2.3.2.linux-amd64.tar.gz | grep -o -E 'href="https://.*?"' | sed -E 's/(href="|"$)//g' | sed -E 's/\&amp;/\&/g'` >> prometheus.tar.gz
curl `curl https://github.com/prometheus/node_exporter/releases/download/v0.16.0/node_exporter-0.16.0.linux-amd64.tar.gz | grep -o -E 'href="https://.*?"' | sed -E 's/(href="|"$)//g' | sed -E 's/\&amp;/\&/g'` >> node_exporter.tar.gz
curl `curl https://github.com/timonwong/uwsgi_exporter/releases/download/v0.7.0/uwsgi_exporter-0.7.0.linux-amd64.tar.gz | grep -o -E 'href="https://.*?"' | sed -E 's/(href="|"$)//g' | sed -E 's/\&amp;/\&/g'` >> uwsgi_exporter.tar.gz
```
И распакуем (считаем, что скачано в одну директорию):  
```
gzip -d *.gz
tar -xf *.tar
```
Также, мне кажется, что логично поместить все эти программы в /opt:  
```
sudo mkdir /opt/monitoring
sudo cp -r node_exporter-0.16.0.linux-amd64 /opt/monitoring/node_exporter
sudo cp -r prometheus-2.3.2.linux-amd64/ /opt/monitoring/prometheus
sudo cp -r uwsgi_exporter-0.7.0.linux-amd64/ /opt/monitoring/uwsgi_exporter
```

2. Добавляем NodeExporter в конфиг (prometheus.yml, см. гитхаб), запускаем все:
```
 - targets: ['localhost:9090','localhost:9100']
```
```
cd /opt/monitoring/node_exporter
./node_exporter &
cd /opt/monitoring/prometheus
./prometheus &
```
Далее все по инструкции из задания, единственная опечатка: http://your-hostname.fintech-admin.m1.tinkoff.cloud **:9090**/targets

3. Добавляем в systemd  
Сначала создаем пользователя и даем ему права на папки:
```
useradd prometheus
cd /opt/monitoring
chown -R prometheus:prometheus *
chmod 0700 prometheus *
```
/etc/systemd/system: кладем .service файлы для node_exporter и prometheus, объединяющий .target - см. гитхаб
```
systemctl start monitoring.target
systemctl enable monitoring.target
```

4. Для выполнения 3его задания переведем uswgi из supervisord в systemd:   
```supervisorctl stop former```  
В /etc/supervisord.d/former.ini ставим autostart=False, далее изменяем /etc/uwsgi.ini, заодно добавляя статистику (см. гитхаб, закомментирован оригинальный конфиг). Секция former сделана, т.к. потом нам нужно будет создавать другие приложения uwsgi  
Запускаем от рута, т.к. порт 80 - привелигированный
```
[former]
#uid = uwsgi
#gid = uwsgi
#emperor = /etc/uwsgi.d
#stats = /run/uwsgi/stats.sock
#chmod-socket = 660
#emperor-tyrant = true
#cap = setgid,setuid

pidfile = /tmp/former.pid
plugins = python
http-socket = 0.0.0.0:80
wsgi-file = /opt/webcode/process/webrunner.py
static-map = /form=/opt/webcode/form/index.html
processes = 5
master = True
vacuum = True
max-requests = 5000

stats-http = True
stats = 127.0.0.1:1717
```
Поскольку конфиг написан в секции former (по умолчанию - uwsgi) => нужно поменять параметры запуска демона. Создаем в /etc/systemd/system папку uwsgi.service.d и кладем туда changes.conf:
```
[Unit]
After=network-online.target

[Service]
ExecStart=
ExecStart=/usr/sbin/uwsgi --ini /etc/uwsgi.ini:former
```

Добавление в prometheus, systemd - аналогично шагу 2
> Путем проб и ошибок было получено, что единственный возможный вариант для systemd записи параметра stats.uri: это --stats.uri=http://localhost:1717. На остальные выдавалась ошибка: "Failed to parse uri \"http://127.0.0.1:1717\": parse \"http://127.0.0.1:1717\": first path segment in URL cannot contain colon.