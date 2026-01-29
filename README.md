📦 Avito Online Trainer Bot

Бот автоматически парсит Avito по всей России, ищет объявления онлайн‑тренеров и отправляет их в Telegram.

🚀 Возможности

- Поиск по всей России (https://avito.ru/rossiya)
- Фильтрация по ключевым словам:
  - тренер, фитнес, спорт, йога, персональный
  - онлайн, дистанционно, zoom, skype
- Отправка объявлений в Telegram:
  - фото
  - цена
  - кнопка "Открыть"
- Хранение просмотренных объявлений (seen.json)
- Антибан задержки
- Рандомизация User-Agent

---

📁 Установка

1. Клонируйте репозиторий

`
git clone https://github.com/yourname/avito-online-trainer-bot.git
cd avito-online-trainer-bot
`

2. Установите зависимости

`
pip install -r requirements.txt
`

3. Создайте файл .env

`
TELEGRAMTOKEN=ВАШТОКЕН
TELEGRAMCHATID=ВАШCHATID
`

4. Запуск

`
python bot.py
`

---

🛠 Автозапуск на сервере

Через systemd:

Создайте файл:

`
sudo nano /etc/systemd/system/avito-bot.service
`

Вставьте:

`
[Unit]
Description=Avito Online Trainer Bot
After=network.target

[Service]
User=root
WorkingDirectory=/root/avito-online-trainer-bot
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
`

Запуск:

`
sudo systemctl daemon-reload
sudo systemctl enable avito-bot
sudo systemctl start avito-bot
`

---

📄 Лицензия

MIT License
