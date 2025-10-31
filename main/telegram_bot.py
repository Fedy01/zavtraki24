import os
import sys
import django
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from asgiref.sync import sync_to_async

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zavtraki24.settings')
django.setup()

from main.models import MenuItem

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши /menu, чтобы увидеть меню.")

# Команда /menu
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем все элементы меню через sync_to_async
    items = await sync_to_async(list)(MenuItem.objects.all())

    if not items:
        await update.message.reply_text("Меню пока пустое 😢")
        return

    message = "🍽 Меню:\n\n"
    for item in items:
        message += f"• {item.name} — {item.price} BYN\n{item.description}\n\n"

    await update.message.reply_text(message)

if __name__ == "__main__":
    TOKEN = "8412427341:AAH1BR1cAxHrUXt9W_qsIqPuxue-bXrXLdg"

    app = ApplicationBuilder().token(TOKEN).build()

    # Регистрируем команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))

    print("Бот запущен...")
    app.run_polling()
