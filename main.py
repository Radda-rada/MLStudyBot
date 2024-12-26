import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bot.handlers import (
    start, help_command, handle_lesson, handle_quiz,
    handle_progress, handle_answer, handle_ask, handle_explain
)
from app import app

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    # Initialize the bot
    application = ApplicationBuilder().token(os.environ.get("TELEGRAM_BOT_TOKEN")).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("lesson", handle_lesson))
    application.add_handler(CommandHandler("quiz", handle_quiz))
    application.add_handler(CommandHandler("progress", handle_progress))
    application.add_handler(CommandHandler("ask", handle_ask))
    application.add_handler(CommandHandler("explain", handle_explain))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()