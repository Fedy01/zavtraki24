from main.models import MenuItem
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from asgiref.sync import sync_to_async

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши /menu, чтобы увидеть меню.")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    items = await sync_to_async(list)(MenuItem.objects.all()[:10])

    if not items:
        await update.message.reply_text("Меню пока пустое 😢")
        return

    message = "🍽 Меню:\n\n"
    for item in items:
        text = f"{item.name}\n{item.description}\n{item.price} BYN"
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Добавить в корзину", callback_data=f"add:{item.id}")]])
        await update.message.reply_text(text, reply_markup=keyboard)
