# ns_v7
1. Библиотеки: requirements/base
pip install -r requirements/base.txt
pip freeze > requirements/base.txt

2. Команды:
БД:
flask db init
flask db migrate
flask db migrate -m "#"
flask db upgrade

Генерация 5 Тренировок Дня:
flask create_wods

Генерация 3 Пользователей:
flask create_users

3. Тесты:
Запуск:
pytest



4. запуск проекта run.py






