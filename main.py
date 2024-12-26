import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bot.handlers import (
    start, help_command, handle_lesson, handle_quiz,
    handle_progress, handle_answer, handle_ask, handle_explain,
    handle_history, handle_meme, handle_stats, handle_user_stats
)
from app import init_db
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the bot with improved error handling and logging."""
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized successfully")

        # Get bot token from environment
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
            return
        else:
            # Log partial token for verification (first 5 chars)
            logger.info(f"Found bot token starting with: {bot_token[:5]}...")

        # Initialize the bot with optimized settings
        logger.info("Initializing bot application...")
        application = ApplicationBuilder().token(bot_token) \
            .concurrent_updates(True) \
            .connection_pool_size(8) \
            .connect_timeout(30) \
            .read_timeout(30) \
            .write_timeout(30) \
            .pool_timeout(30) \
            .build()
        logger.info("Bot application built successfully")

        # Add handlers with logging
        logger.info("Adding command handlers...")
        handlers = [
            CommandHandler("start", start),
            CommandHandler("help", help_command),
            CommandHandler("lesson", handle_lesson),
            CommandHandler("quiz", handle_quiz),
            CommandHandler("progress", handle_progress),
            CommandHandler("ask", handle_ask),
            CommandHandler("explain", handle_explain),
            CommandHandler("history", handle_history),
            CommandHandler("meme", handle_meme),
            CommandHandler("stats", handle_stats),
            CommandHandler("user_stats", handle_user_stats),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)
        ]

        for handler in handlers:
            application.add_handler(handler)
            if isinstance(handler, CommandHandler):
                logger.info(f"Added handler for commands: {handler.commands}")
            else:
                logger.info("Added message handler for text messages")

        logger.info("All handlers added successfully")
        logger.info("Bot initialized successfully, starting polling...")

        # Start the bot with optimized settings
        application.run_polling(
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True
        )

    except Exception as e:
        logger.error(f"Critical error in bot initialization: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()