

[![Built and pushed to docker hub](https://github.com/Ridmel/foodgram-project-react/actions/workflows/push_image_to_dockerhub.yml/badge.svg?branch=master)](https://github.com/Ridmel/foodgram-project-react/actions/workflows/push_image_to_dockerhub.yml)

## Foodgram

    Временно развернут на IP: 51.250.81.146

Сайт-площадка, где каждый может создать и разместить свои самые вкусные рецепты. 

Стек технологий: Django, Django REST framework, PostgreSQL, Nginx, Gunicorn, Docker, Github actions/workflow  
<br/>
<br/>
  
  
#### Запуск демо-версии:
*(для развертывания необходим *docker compose v2+*)*  
Выполнить из директории `/infra/`:

    (sudo) make run_demo
Сайт будет доступен по локальному адресу `127.0.0.1`.
База данных демо-версии предзаполнена, в ней зарегистрированы два пользователя - с админскими правами и без:
 - ***user***  
		логин: `user@user.com`  
		пароль: `user`  
- ***admin***  
		логин: `admin@admin.com`  
    		пароль: `admin`

<br/>

<img src="https://user-images.githubusercontent.com/80767090/170669580-95943292-55b9-4067-bfba-d7416c561dbb.png" alt="Your image title" width="500"/>

<br/>

#### Запуск версии с чистой БД:  
*(для развертывания необходим *docker compose*)*  
Создать файл `.env` в каталоге `/infra/` с необходимыми переменными окружения (пример в файле `/infra/.env.example`).
Выполнить из директории `/infra/`:

    (sudo) make run_new
    make create_user
<br/>
<br/>
<br/>  

*Автор: Роман Сергиенко* 