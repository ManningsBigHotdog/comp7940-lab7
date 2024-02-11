from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import configparser
import logging
import redis
from ChatGPT_HKBU import HKBU_ChatGPT

# Initialize the Redis client globally.
global redis1

def main():
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    
    # Initialize the Redis client.
    global redis1
    redis1 = redis.Redis(host=(config['REDIS']['HOST']), password=(config['REDIS']['PASSWORD']), port=(config['REDIS']['REDISPORT']))
   
    # Set up the logging module.
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # Initialize your HKBU_ChatGPT instance.
    global chatgpt
    chatgpt = HKBU_ChatGPT(config)
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)

    # Command handlers for different functionalities.
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("hello", hello))  # Add handler for /hello command.

    # Start the bot.
    updater.start_polling()
    updater.idle()

def equiped_chatgpt(update: Update, context: CallbackContext) -> None:
    # Send a "processing" message to the user.
    processing_message = context.bot.send_message(chat_id=update.effective_chat.id, text="Processing your request...")
    reply_message = chatgpt.submit(update.message.text)
    
    # Log the update and context information.
    logging.info(f"Update: {update}")
    logging.info(f"context: {context}")

    # Edit the message with the response from the chatbot.
    context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=processing_message.message_id, text=reply_message)

def add(update: Update, context: CallbackContext) -> None:
    try:
        global redis1
        msg = context.args[0]  # /add keyword <-- this should store the keyword.
        redis1.incr(msg)
        update.message.reply_text(f'You have said {msg} for {redis1.get(msg).decode("UTF-8")} times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')

def hello(update: Update, context: CallbackContext) -> None:
    """Reply with 'Good day, <name>!' when the command /hello is issued."""
    try:
        name = ' '.join(context.args)
        if name:
            update.message.reply_text(f'Good day, {name}!')
        else:
            update.message.reply_text('Good day!')
    except (IndexError, ValueError):
        update.message.reply_text('Good day!')

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Helping you helping you.')


if __name__ == '__main__':
    main()