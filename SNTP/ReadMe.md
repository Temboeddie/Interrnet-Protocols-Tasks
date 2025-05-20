Установите смещение времени в `config.txt`
Запустите сервер:

python sntp_server.py

Вы должны увидеть:
SNTP server running on port 123 with offset 10 seconds

Запуск клиента:
python sntp_client.py
Это отправит двоичный SNTP-запрос на сервер и выведет полученное измененное время.
