### Домашнее задание 9 - nginx

1. Я начал выполнять задание еще до публикации рекомендаций, поэтому скомпилировал "по-простому". В следующий раз буду работать с rpm-пакетами.   
```
wget http://nginx.org/download/nginx-1.10.1.tar.gz
gzip -d nginx-1.10.1.tar.gz
tar -x nginx-1.10.1.tar
git clone git://github.com/vozlt/nginx-module-vts.git
yum install -y httpd-devel pcre perl pcre-devel zlib zlib-devel GeoIP GeoIP-devel
./configure --add-module=./../nginx-module-vts/
make install
```

И для удобства:  
```
cd /sbin
ln /usr/local/nginx/sbin/nginx nginx
```
Запускать nginx придется от root, т.к. требуется 80, привелигерованный порт. service-файл от systemd на гитхабе.

2. В приложенных конфигах на гитхабе сразу выполнены оба задания. В данной версии nginx в /etc/nginx/config.d не устанавливается default.conf, поэтому я переписал /usr/local/nginx/conf/nginx.conf с включением всех из этой директории (на гитхабе)  
Для доступа к test-1 и test-2 был исправлен файл hosts. Я пытался сделать через DNS, но resolve.conf формируется автоматически и DNS-сервера из него не подгружаются даже после service network reload

3. Посмотреть модули, с которыми скомпилирован nginx:
```
$ nginx -V
nginx version: nginx/1.10.1
built by gcc 4.8.5 20150623 (Red Hat 4.8.5-28) (GCC)
configure arguments: --add-module=./../nginx-module-vts/
```

4. Замечания:  
- Аналогично uwsgi можно поднять модуль на Graphana, но там неправильные названия метрик  
- Задание про балансировку я бы хотел оставить на случай двух django приложений, все равно там придется использовать upstream  
- Кроме того, возникает проблема: nginx не запускается через systemd: "PID file /tmp/nginx.pid not readable (yet?) after start", сейчас тоже гуглю, разбираюсь. Возможно, это связано с другой проблемой: nginx не хочет переходить в состояние running и из-за этого через некоторое время закрывается. Тоже постараюсь разобраться к следующему заданию, скорее всего, это мое неумение обращаться с systemd.     