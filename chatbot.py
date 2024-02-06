import configparser
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text.upper())

def main():
    """Start the bot."""
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')
    token = config['TELEGRAM']['ACCESS_TOKEN']

    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on non-command i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
