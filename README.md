# Main-API-server

### Установка

Нужно использовать pip для установки.

``` pip install -r requirements.txt ```

### Запуск

``` uvicorn main:app --reload port=port host=host ```

### О приложении

Содержит 4 модуля: 
1. resumes
2. templates
3. mail
4. users

resumes — работа с резюме, загрузкой/выгрузкой
templates — работа с шаблонами
mail — работа с отправкой сообщения по почте
users — работа с пользователями

Каждый модуль имеет следующую структуру:

service.py — файл реализации функций
router.py — файл создания маршрутов
schemas.py — файл хранения входных и выходных классов
models.py — файл создания моделей БД

AbstractModel.py хранит абстрактную модель для подключения к БД
exceptions.py — файл для вызова результата
jwt_handler.py — реализация проверки пользователя по JWT токену

Использовано:
FastAPI, SQLAlchemy, Redis, PgBouncer
