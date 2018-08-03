## Домашнее задание №5 - HTTP

1. Строка для запуска приложения  
> uwsgi  
>	--plugins=python  **Используемые плагины для запуска приложений**  
>	--http-socket=0.0.0.0:80  **Адрес, который будет прослушиваться wsgi-сервером**  
>	--wsgi-file /opt/webcode/process/webrunner.py  **Исполняемый файл wsgi**  
>	--static-map /form=/opt/webcode/form/index.html  **Предоставление доступа к определенной локальной директории/файлу по заданному адресу**  
>	--processes=5  **Количество worker-ов - процессов, обрабатывющих запросы**  
>	--master  **Запуск управляющего процесса (который может перезапустить worker-ы без закрытия сокета)**  
>	--pidfile=/tmp/formdig.pid  **Расположение pid-файла**  
>	--vacuum  **Закрывать все файловые дескрипторы при выходе**  
>	--max-requests=5000  **Перезапуск worker-а после определенного количества запросов**  
2. Адрес доступа к форме
> http://s-15.fintech-admin.m1.tinkoff.cloud/form
3. Изменение метода на GET  
Измененный файл - index.html на гитхабе  
Ответ сервера (http://s-15.fintech-admin.m1.tinkoff.cloud/process?Name=Fedor&Age=22):  
> Method: GET
> Get content: /process?Name=Fedor&Age=22
> Post content: 
4. Описание опций - см. пункт 1  
Описание конфига и webrunner.py - см. соответствующие файлы