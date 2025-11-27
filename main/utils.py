import requests
from django.conf import settings
from telegram import Bot


def send_order_notification(order):
    token = settings.TELEGRAM_BOT_TOKEN
    admin_chat = settings.TELEGRAM_ADMIN_CHAT_ID
    if not token or not admin_chat:
        return

    bot = Bot(token=token)
    text = f"Новый заказ #{order.id}\nИмя: {order.name}\nТелефон: {order.phone}\nАдрес: {order.address}\n\nПозиции:\n"
    for it in order.items.all():
        text += f"- {it.item.name} × {it.quantity}\n"

    total = sum(it.item.price * it.quantity for it in order.items.all())
    text += f"\nСумма: {total} BYN"

    bot.send_message(chat_id=admin_chat, text=text)



def tg_send(chat_id, text):
    token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text})
    except Exception as e:
        print("Telegram error:", e)


def notify_new_order(order):
    text = (
        f"🆕 НОВЫЙ ЗАКАЗ #{order.id}\n"
        f"Имя: {order.name}\n"
        f"Телефон: {order.phone}\n"
        f"Адрес: {order.address}\n"
        f"Статус: {order.get_status_display()}\n"
        f"---\n"
        "Позиции:\n"
    )
    for it in order.items.all():
        text += f"{it.item.name} × {it.quantity}\n"

    tg_send(settings.TELEGRAM_ADMIN_CHAT_ID, text)

def notify_client(order, text):
    if order.telegram_chat_id:
        tg_send(order.telegram_chat_id, text)