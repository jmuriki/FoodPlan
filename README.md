# FoodPlan

Сайт предлагает сервис выдачи рецептов по приготовлению блюд, планированию рациона и затрат на еду.

## Запуск в режиме разработчика

- Скачайте код
```bash
git clone https://github.com/jmuriki/FoodPlan.git
cd FoodPlan
```

- Создайте и активируйте виртуальное окружение (необязательно, но рекомендуется):
*nix или MacOS:
```bash
python3 -m venv venv
source venv/bin/activate
```
Windows:
```bash
python -m venv env
source env/bin/activate
```
- Установите зависимости
```bash
pip install -r requirements.txt
```

- Создайте файл .env и вставьте в него следующие строки:
```bash
DJANGO_DEBUG=True
```

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
