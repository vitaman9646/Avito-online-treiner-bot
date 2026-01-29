import os
import re
import json
import time
import random
import logging
from pathlib import Path
from typing import Set

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv


# -----------------------------
# ЗАГРУЗКА .env
# -----------------------------
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")  # ← ВСТАВЬ СВОЙ ТОКЕН В .env
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # ← ВСТАВЬ СВОЙ CHAT_ID В .env

if not TOKEN or not CHAT_ID:
    raise SystemExit("❌ TELEGRAM_TOKEN или TELEGRAM_CHAT_ID отсутствуют в .env")


# -----------------------------
# ЛОГИ
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-5s  %(message)s",
)
logger = logging.getLogger(__name__)


# -----------------------------
# TELEGRAM API
# -----------------------------
def tg(method: str, data: dict):
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        logger.error(f"Ошибка Telegram: {e}")


def notify(text: str):
    tg("sendMessage", {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    })


def notify_photo(url: str, caption: str):
    tg("sendPhoto", {
        "chat_id": CHAT_ID,
        "photo": url,
        "caption": caption,
        "parse_mode": "HTML",
    })


def notify_link_button(link: str):
    tg("sendMessage", {
        "chat_id": CHAT_ID,
        "text": "🔗 Объявление",
        "reply_markup": json.dumps({
            "inline_keyboard": [[{"text": "Открыть", "url": link}]]
        })
    })


# -----------------------------
# ХРАНЕНИЕ ПРОСМОТРЕННЫХ ID
# -----------------------------
SEEN_FILE = Path("seen.json")

if SEEN_FILE.exists():
    seen: Set[str] = set(json.loads(SEEN_FILE.read_text()))
else:
    seen: Set[str] = set()


def save_seen():
    SEEN_FILE.write_text(json.dumps(list(seen)))


# -----------------------------
# ПАРСИНГ ВСЕЙ РОССИИ
# -----------------------------
def parse_russia():
    try:
        url = f"https://www.avito.ru/rossiya?q=тренер&_{random.randint(100000, 999999)}"
        logger.info(f"→ RUSSIA  {url}")

        headers = {
            "User-Agent": random.choice([
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2) Safari/604.1",
                "Mozilla/5.0 (Linux; Android 14; SM-S928B) Chrome/122.0 Mobile",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) Safari/605.1",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0",
            ])
        }

        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        items = soup.select("div[data-marker='item']")

        for item in items:
            try:
                item_id = item.get("data-item-id")
                if not item_id or item_id in seen:
                    continue

                title_el = item.select_one("h3")
                if not title_el:
                    continue
                title = title_el.text.strip()

                # Фильтр профессии
                is_trainer = re.search(r"тренер|фитнес|спорт|йога|персональн", title.lower())

                # Фильтр онлайн
                is_online = re.search(r"онлайн|дистанц|zoom|скайп|skype|online", title.lower())

                if not (is_trainer and is_online):
                    continue

                price_el = item.select_one("meta[itemprop='price']")
                price = int(price_el.get("content")) if price_el else 0

                link_el = item.select_one("a")
                if not link_el:
                    continue
                link = "https://www.avito.ru" + link_el.get("href")

                # Фото
                img = (
                    item.select_one("img.photo-slider-list__image")
                    or item.select_one("img.iva-item-slider-image")
                    or item.select_one("img")
                )
                photo = img.get("src") or img.get("data-src") if img else None

                # Формируем сообщение
                caption = (
                    f"<b>КЛИЕНТ • ОНЛАЙН</b>\n\n"
                    f"{title}\n"
                    f"💰 {price:,} ₽\n\n"
                    f"<a href=\"{link}\">Открыть объявление</a>\n"
                    f"🔥 <b>ОТВЕЧАЙ БЫСТРО!</b>"
                )

                # Отправляем фото или текст
                if photo:
                    notify_photo(photo, caption)
                else:
                    notify(caption)

                # Кнопка
                notify_link_button(link)

                # Сохраняем ID
                seen.add(item_id)
                save_seen()

                logger.info(f"Найден онлайн-клиент → {title[:70]}")

                # Антибан задержка
                time.sleep(random.uniform(1.5, 3.5))

            except Exception as e:
                logger.error(f"Ошибка парсинга: {e}")

    except Exception as e:
        logger.error(f"Ошибка запроса: {e}")


# -----------------------------
# ОСНОВНОЙ ЦИКЛ
# -----------------------------
def main():
    while True:
        parse_russia()

        delay = random.randint(20 * 60, 35 * 60)
        logger.info(f"Цикл завершён → следующий через ~{delay // 60} мин")
        time.sleep(delay)


if __name__ == "__main__":
    main()
