#!/bin/bash

#Two formers for upstream
/usr/sbin/uwsgi --ini /etc/uwsgi.ini:former --http-socket=0.0.0.0:8080 --stats-http=True --stats=127.0.0.1:1717 &
/usr/sbin/uwsgi --ini /etc/uwsgi.ini:former --http-socket=0.0.0.0:8081 &

