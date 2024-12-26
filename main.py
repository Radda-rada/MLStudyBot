import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bot.handlers import (
    start, help_command, handle_lesson, handle_quiz,
    handle_progress, handle_answer, handle_ask, handle_explain,
    handle_history, handle_meme
)
from app import init_db

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    # Initialize database
    init_db()

    # Initialize the bot with optimized settings
    application = ApplicationBuilder().token(
        os.environ.get("TELEGRAM_BOT_TOKEN")
    ).concurrent_updates(True).connection_pool_size(8).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("lesson", handle_lesson))
    application.add_handler(CommandHandler("quiz", handle_quiz))
    application.add_handler(CommandHandler("progress", handle_progress))
    application.add_handler(CommandHandler("ask", handle_ask))
    application.add_handler(CommandHandler("explain", handle_explain))
    application.add_handler(CommandHandler("history", handle_history))
    application.add_handler(CommandHandler("meme", handle_meme))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))

    # Start the bot with optimized settings
    application.run_polling(
        pool_timeout=30,
        read_timeout=30,
        write_timeout=30,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()