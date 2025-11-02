from main.models import MenuItem
from telegram import Update
from telegram.ext import ContextTypes
from asgiref.sync import sync_to_async

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши /menu, чтобы увидеть меню.")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    items = await sync_to_async(list)(MenuItem.objects.all())

    if not items:
        await update.message.reply_text("Меню пока пустое 😢")
        return

    message = "🍽 Меню:\n\n"
    for item in items:
        message += f"• {item.name} — {item.price} BYN\n{item.description}\n\n"

    await update.message.reply_text(message)
