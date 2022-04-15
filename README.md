# "Продуктовый Помошник" - сервис для публикации и обмена рецептами (еды)


На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Проект предназначен для развёртывания в Docker [Get Docker](https://docs.docker.com/get-docker/)


![](https://img.shields.io/badge/python-3.8-blue)
![](https://img.shields.io/badge/django-4.0-green)
![](https://img.shields.io/badge/DRF-3.2-red)
![Продуктовый Помошник CI/CD](https://github.com/wrawka/foodgram-project-react/actions/workflows/main.yml/badge.svg)

### Переменные окружения (локальный деплой)

Переименовать файл **infra/.env.template** >>> **.env**

Задать значения переменных для доступа в соответствии с шаблоном:

```
SECRET_KEY=  # секретный ключ Django
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
```

### Развёртывание через docker-compose

```bash
docker-compose -f .\docker-compose.yaml up
```
### Миграции в базу данных

```bash
docker exec -it <id контейнера "backend"> python manage.py migrate
```

### Создание суперпользователя

```bash
docker exec -it <id контейнера "backend"> bash
python manage.py createsuperuser
```

### Заполнение базы данных из JSON

В папке **fixtures** доступны исходные данные для тегов, и ингредиентов рецептов.

```bash
docker exec -it <id контейнера "backend"> python manage.py loaddata fixtures/*.json
```