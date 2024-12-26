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

async def setup_bot(application):
    """Initial bot setup including profile photo."""
    try:
        bot = application.bot
        # Check if file exists
        photo_path = 'attached_assets/Иллюстрация_без_названия.jpg'
        if not os.path.exists(photo_path):
            logger.error(f"Profile photo file not found at {photo_path}")
            return

        # Get file size
        file_size = os.path.getsize(photo_path)
        logger.info(f"Profile photo file size: {file_size} bytes")

        # Check file permissions
        logger.info(f"Checking file permissions for {photo_path}")
        try:
            with open(photo_path, 'rb') as photo:
                # Read file content
                photo_content = photo.read()
                logger.info(f"Successfully read photo file, content size: {len(photo_content)} bytes")
                # Set profile photo
                await bot.set_profile_photo(photo=photo_content)
                logger.info("Successfully set bot profile photo")
        except IOError as io_error:
            logger.error(f"IO Error reading photo file: {str(io_error)}")
            return
    except Exception as e:
        logger.error(f"Failed to set bot profile photo: {str(e)}")
        if hasattr(e, 'message'):
            logger.error(f"Error message: {e.message}")

def main():
    # Initialize database
    init_db()

    # Initialize the bot
    application = ApplicationBuilder().token(os.environ.get("TELEGRAM_BOT_TOKEN")).build()

    # Setup bot profile
    application.job_queue.run_once(setup_bot, when=1, data=application)

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

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()