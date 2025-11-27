import os
import sys
import django
from telegram.ext import ApplicationBuilder, CommandHandler

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zavtraki24.settings")
django.setup()

from .handlers import start, menu

TOKEN = "8412427341:AAH1BR1cAxHrUXt9W_qsIqPuxue-bXrXLdg"

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("menu", menu))

print("Бот запущен...")
app.run_polling()

# Чтобы запустить бота сначало надо запустить сервак а потом написать "python -m bot.bot"