## Домашняя работа №8 - PostgreSQL_2

1. Сначала создадим 2 базы данных для нашей работы: для заданий на индексы и на PeeWee
```
psql -U postgres -p 6789
CREATE DATABASE shop_data_1;
GRANT ALL PRIVILEGES ON DATABASE "shop_data_1" to sample_user;
CREATE DATABASE psql_test;
```
Дадим соответствующие разрешения пользователю sample_user в pg_hba.conf (на подключение к shop_data_1), перезапускаем сервис

Установим peewee:
```
pip3.6 install peewee
```

2. Python-файл - см. гитхаб. Значение функций как в предыдущем д/з.  
Чтобы работать со скриптом как с библиотекой, необходимо использовать не класс ShopDatabase, а объект ShopDatabaseObject

3. Краткая выжимка об индексе - B-tree.pdf