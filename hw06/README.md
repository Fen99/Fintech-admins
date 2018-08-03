## Домашнее задание №6 - Базы данных. PostgreSQL (введение)

1. Устанавливаем PostgreSQL:  
```yum install -y postgresql-server```

2. Инициализируем рабочую директорию pgsql:  
```sudo postgresql-setup initdb```  
По умолчанию это будет директория /var/lib/pgsql/data/


3. Конфигурируем (postgresql.conf и pg_hba.conf см. в этой директории на github). В postgresql.conf:  
```
listen_addresses = '*' 
post = 6789
shared_buffers = 512MB
work_mem = 32MB
```

4. Для автозапуска - systemd  
Нам придется немного поменять правила запуска, потому что параметр -p в pg_ctl приоритетнее, чем конфиг, а строка в исходном файле postgresql.service выгядит как:
```
Environment=PGPORT=5432
ExecStart=/usr/bin/pg_ctl start -D ${PGDATA} -s -o "-p ${PGPORT}" -w -t 300
```
Но менять в ~lib/systemd/system - дурной тон. Поэтому создаем директорию postgesql.service.d в /etc/systemd/system, куда кладем конфиг с изменениями (changes.conf, на гитхабе): 
```
ExecStart=/usr/bin/pg_ctl start -D ${PGDATA} -s -o -t 30
```

После всего: 
```
sudo systemctl start postgresql  
sudo systemctl enable postgresql  
```

> Комментарии:  
> /etc/systemd/system/ - для кастомизации конфигов/пользовательских юнитов, ~lib/systemd/system - для устанавливаемых автоматически   
> В нашем случае мы можем либо изменить конфиг, создав в модифицированный конфиг /etc/systemd/system/postgresql.service, либо это может использоваться для создания второго экземпляра postgresql-сервиса, в любом случае не нужно забывать начинать конфиг с ".include /lib/systemd/system/postgresql.service"  
> Отличие создание директории postgresql.service.d от конфига создания конфига postgresql.service: файлы в директории расширяют конфиг, а не перезаписывают его => include не требуется  
> Для перезаписи сначала следует написать, например "ExecStart=", а потом уже нужную опцию  

5. Подключаемся и создаем БД, пользователя, даем ему привелегии  
```
psql -U postgres -p 6789
ALTER USER postgres PASSWORD 'postgres'; (пароль, чтобы отказаться от trust)
CREATE DATABASE shop_data;
CREATE USER sample_user WITH PASSWORD 'qwerty';
GRANT ALL PRIVILEGES ON DATABASE "shop_data" to sample_user;
```

6. pg_hba.conf:
```
local   all             postgres                                password
#host    all             all             127.0.0.1/32           trust
host    all             postgres        127.0.0.1/32            password
# Our sample user
host    shop_data       sample_user     127.0.0.1/32            md5
host    shop_data       sample_user     0.0.0.0/0               md5  
```
И перазапускам сервис

7. Скрипт python - в директории python на github   
Для работы нужно создать объект класса ShopDatabase и использовать его методы (подключение создается во время init):   
CreateTables - создает таблицы из задания   
CreateSampleData - наполняет таблицы данными (примерами)   
AddToOrder - добавляет товар в заказ   
RemoveFromOrder - удаляет товар из заказа   
ChangeCount - изменяет количество товара в заказе   
Dump - создает дамп заказов  
