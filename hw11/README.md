### Домашняя работа 11 - TeamCity

1. Создаем приватные ключи - puttygen (ранее я уже создавал, сейчас просто экспортируем в SSH-формат для TeamCity).
> Публичный ключ загружаем в bitbucket, а ранее он был загружен в ~/.ssh/authorized_keys

2. systemd reload для django и uwsgi нужно будет делать от нашего пользователя (user15) => нужно добавить ему такое разрешение перезапускать данные сервисы без пароля (но с помощью sudo)
Дописываем в /etc/sudoers.d/user15:
```
Cmnd_Alias WEBSERVER_RESTART_CMNDS = /bin/systemctl restart uwsgi@[123456789].service, /bin/systemctl restart django.service
user15 ALL=(ALL) NOPASSWD: WEBSERVER_RESTART_CMNDS
```

3. Репозитории и build-конфигурация former.  
http://bitbucket.fintech-admin.m1.tinkoff.cloud/scm/usr15/former.git  
http://bitbucket.fintech-admin.m1.tinkoff.cloud/scm/usr15/addressbook.git  

- Создаем репозитории former, django, копируем туда исходные файлы, делаем коммит.  
- В TeamCity - FormerBuild - build configuration. 
- Artifacts path: **/* => release
- Version control settings (VCS): Changes checking interval: 10s
- VCS Trigger: "+:*"
- Добавляем build step PutVCSNumber (command line):
```  
#!/bin/bash
echo "%build.vcs.number%" > vcs_number
```  
- Запускаем build, проверяем, что все хорошо.

4. Deploy-конфигурация former
- Добавляем зависимости, в artifact dependency правило "+:release=>release"
- Добавляем Build step SSH upload, target: s-15.fintech-admin.m1.tinkoff.cloud:/opt/webcode, source: release/**, используем ранее загруженный приватный ключ
- Добавляем SSH-exec, используем загруженный ключ (2 сервиса, т.к. они балансируются еще с момента задания по nginx):
```
sudo systemctl restart uwsgi@1.service
sudo systemctl restart uwsgi@2.service
```
- Добавляем Finish build trigger на FormerBuild
- Пробуем сделать build, проверяем, что все работает
- Проверяем, что commit вызывает всю цепочку

5. Добавляем pylint (build step - command line)
```
#!/bin/bash
echo Pylint log > pylint.log

# echo because pylint returns code 20
echo $(pylint $(find | sed -e 's/.\///' | grep .*\.py) >> pylint.log)
```

6. Добавляем PR CI/CD (и для former, и для django)
- "+:refs/(pull-requests/*)/merge" - branch specification VCS Root
- +:pull-requests/* и +:<default> - VCS filter в конфигурации build. default обязательно, иначе нечего будет делать deploy
- В Deploy-конфигурации оставляем +:<default>

7. Экстрагируем шаблоны, создаем на основании них для django, проверяем
- Заодно шаблонизируем %application_dir%, чтобы не менять целиком SSH-upload
- Для сервиса django ставим владельца user15 и ему же переназначаем директорию