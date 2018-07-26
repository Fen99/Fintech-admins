## Домашнее задание №6 - Базы данных. PostgreSQL (введение)

1. Устанавливаем PostgreSQL:
> yum install -y postgresql-server

2. Создаем рабочую директорию pgsql:
> Команды выполняются в директории /usr/local
> sudo -u postgres mkdir pgsql
> sudo chown postgres pgsql
> sudo chown :postgres pgsql
> sudo chmod 0770 pgsql
> su postgres -c 'initdb -D /usr/local/pgsql/data'

3. Конфигурируем (postgresql.conf и pg_hba.conf см. в этой директории на github):
> В postgresql.conf:
> listen_addresses = '*' 
> post = 6789
> shared_buffers = 512MB
> work_mem = 32MB

4. Для автозапуска - systemd
> Команды от root в /etc/systemd/system/
> mkdir postgresql.service.d
> Создаем там файл custom.conf (см. в этой директории на github)
> systemctl start postgresql.service
> systemctl enable postgresql.service (запуск при старте)
>> Не Type=notify, т.к., похоже, стандартный пакет скомпилирован без --with-systemd
>> Пустая строка: "ExecStart=" - согласно https://github.com/moby/moby/issues/14491
>> Обязательно добавляем в окружение PGDATA, т.к. в systemd нельзя нормально передать аргументы

5. Подключаемся и создаем БД, пользователя, даем ему привелегии
> psql -U postgres -p 6789
> ALTER USER postgres PASSWORD 'postgres'; (пароль, чтобы отказаться от trust)
> CREATE DATABASE shop_data;
> CREATE USER sample_user WITH PASSWORD 'qwerty';
> GRANT ALL PRIVILEGES ON DATABASE "shop_data" to sample_user;

6. pg_hba.conf:
> local   all             postgres                                password
> #host    all             all             127.0.0.1/32           trust
> host    all             postgres        127.0.0.1/32            password
> # Our sample user
> host    shop_data       sample_user     127.0.0.1/32            md5
> host    shop_data       sample_user     0.0.0.0/0               md5  
И перазапускам сервис

7. Скрипт python - в директории python на github  
Для работы нужно создать объект класса ShopDatabase и использовать его методы (подключение создается во время init):  
CreateTables  
CreateSampleData  
AddToOrder  
RemoveFromOrder  
ChangeCount  
Dump  