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
SECRET_KEY=вставьте_secret_key
DEBUG=True
SENDER_EMAIL=email_для_отправки_с_него_технических_сообщений_клиентам
SENDER_PASSWORD=пароль_от_email
ONE_MONTH_PRICE=стоимость_подписки_на_один_месяц
THREE_MONTHS_PRICE=стоимость_подписки_на_три_месяца
SIX_MONTHS_PRICE=стоимость_подписки_на_шесть_месяцев
TWELVE_MONTHS_PRICE=стоимость_подписки_на_двенадцать_месяцев
DISCOUNT=размер_скидки_по_умолчанию
SHOP_KEY=ключ_yookassa
SHOP_SECRET_KEY=пароль_yookassa
REDIRECT_URL=адрес_редиректа_после_успешной_оплаты
```

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
