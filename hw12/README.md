### Домашняя работа 12 - Zabbix

1. Устанавливаем zabbix+mysql как в задании
```
sudo rpm -ivh https://repo.zabbix.com/zabbix/3.4/rhel/7/x86_64/zabbix-release-3.4-2.el7.noarch.rpm
sudo yum-config-manager --enable rhel-7-server-optional-rpms
sudo yum install zabbix-server-mysql
```
Нужно решить проблему с конфликтом версий php:
```
sudo yum remove php*
sudo yum install php56u-xml
sudo yum install --skip-broken zabbix-web-mysql
```
Финальные штрихи (пароль root для MariaDB - password, порт по умолчанию - 3306):
```
sudo yum install mariadb mariadb-server
sudo systemctl start mariadb && sudo systemctl enable mariadb.service
sudo /usr/bin/mysql_secure_installation
```

2. Настройка базы данных
```
mysql -uroot -ppassword
create database zabbix character set utf8 collate utf8_bin;
grant all privileges on zabbix.* to zabbix@localhost identified by 'zabbix_password';
quit;
```

3. Подготовка базы данных для zabbix
```
sudo zcat /usr/share/doc/zabbix-server-mysql*/create.sql.gz | mysql -uroot -ppassword zabbix
```
И исправляем конфиг /etc/zabbix/zabbix_server.conf:
```
DBPassword=zabbix_password
DBHost=localhost
```

4. Zabbix в systemd  
Создаем /etc/systemd/system/zabbix-server.service.d/changes.conf (на гитхабе), где прописываем WantedBy=monitoring.target. enable будет автоматически, т.к. monitoring.target запускается с системой
```
sudo systemctl start zabbix-server
```

5. Настройка httpd.  
Меняем часовой пояс, ставим httpd слушать порт 8800 (т.к. 80 занят nginx) - конфиги на гитхабе
```
sudo systemctl start httpd 
sudo systemctl enable httpd
```
Настраиваем zabbix. 10051 - порт zabbix  
Заходим, default пароль оставляем (zabbix) для удобства

6. zabbix-agent
```
sudo yum install zabbix-agent.x86_64
```
Параметры используются по умолчанию. Аналогично zabbix добавляем в monitoring.target

7. Кастомная метрика   
Создаем файл /etc/zabbix/zabbix_agentd.d/userparameter_postgresql.conf, настраиваем таймаут агента, устанавливаем zabbix-get.  
В userparameter_postgresql.conf вносим изменения (на гитхабе): т.к. запретили trust, то спрашиваем пароль, в настройки pgsql.version тоже добавляем параметры  
Проверяем:
```
$ zabbix_get -s 127.0.0.1 -k pgsql.version[6789,postgres,postgres]
server_version----------------9.2.24(1row)
$ zabbix_get -s 127.0.0.1 -k pgsql.ping[6789,postgres,postgres]
10
```
Настраиваем в графическом интерфейсе, проверяем, что все работает.
- Если произошла опечатка в имени метрики, то его нужно пересоздать, иначе он работать не будет

8. Zabbix Trapper  
Добавляем метрику random-number, устанавливаем zabbix-sender, отправляем данные из консоли, проверяем, что они появились в LastData
```
while true; do zabbix_sender -z 127.0.0.1 -p 10051 -s "Zabbix server" -k pgsql.random -o $(( ( RANDOM % 100 )  + 1 )); sleep 10; done;
```
Настраиваем триггер Random number trigger с условием "{Zabbix server:pgsql.random.last()}>0" в том же шаблоне (>0, чтобы точно срабатывал)

9. Добавляем правило обнаружения  
Нужно исправить - поскольку нет trust-авторизации, то в обе метрики добавляем port, user, password. Немного исправленные варианты метрик:
```
# На строки конфиг разделен здесь для удобства

# Построение json вида
# {
#	"data":	
#		[ 
#			{"{#DATABASE}":"postgres"},
#			<...>
#			{"{#DATABASE}":"ans_pgtest"},
#			{} 
#		]
# }
# При этом строку string_add, строку из "-", строку "... row(s))" нужно выкинуть

UserParameter=pgsql.database.discovery[*],
echo -n '{"data":[ ';
for db in $(PGPASSWORD="$3" psql -U "$2" -p "$1" -c "SELECT string_agg(datname,' ') from pg_catalog.pg_database where datistemplate = 'false'" | grep -Ev -e 'string_agg' -e '^\-+$' -e 'row.*\)');
	do echo -n '{"{#DATABASE}":"'$db'"}, '
; done; echo '{} ]}';

# Возвращает размер базы данных, заданной в 4 параметре. Выделяет только его (удаляет лишние строки)
UserParameter=pgsql.database.size[*],
PGPASSWORD="$3" psql -U "$2" -p "$1"  -c "SELECT pg_database_size(datname) FROM pg_catalog.pg_database WHERE datistemplate = 'false' AND datname = '$4'" | grep -o -E '[0-9]+$'
```
Условием триггера ставим размер, больший 7*1024*1024 - БД addressbook даст warning

10. Graphana
Активируем плагин zabbix, добавляем Zabbix data source (создаем ограниченного пользователя graphana, пароль graphana), активируем Dashboard