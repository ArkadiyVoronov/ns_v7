# ns_v7
1. Библиотеки: requirements/base
pip install -r requirements/base.txt
pip freeze > requirements/base.txt

2. Коммманды:
БД:
flask db init
flask db migrate
flask db migrate -m "#"
flask db upgrade

БД генерация 5 Тренировк Дня:
flask create_wods

3. Тесты:
Запуск:
python -m unittest discover -s tests



4. запуск проекта run.py






