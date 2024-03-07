import os
from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, 
                          CallbackContext)
# import configparser
import logging
import redis
from ChatGPT_HKBU import HKBU_ChatGPT

global redis1
def main():
    # Load token 
    config = configparser.ConfigParser()
    config.read('config.ini')
    # updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    updater = Updater(token=(os.environ.get('TG_ACCESS_TOKEN')), use_context=True)
    dispatcher = updater.dispatcher
    global redis1
    # redis1 = redis.Redis(host=(config['REDIS']['HOST']), password=(config['REDIS']['PASSWORD']), port=(config['REDIS']['REDISPORT']))
    redis1 = redis.Redis(host=(os.environ.get('REDIS_HOST')), password=(os.environ.get('REDIS_PASSWORD')), port=(os.environ.get('REDIS_PORT')))
   
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # dispatcher for chatgpt
    global chatgpt
    chatgpt = HKBU_ChatGPT(config)
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello))
    dispatcher.add_handler(CommandHandler("echo", echo))
    
    # To start the bot:
    updater.start_polling()
    updater.idle()

def equiped_chatgpt(update: Update, context: CallbackContext) -> None:
    try:
        processing_message = context.bot.send_message(chat_id=update.effective_chat.id, text="Processing your request...")
        logging.info(f"Received prompt {{ {update.message.text} }}, Sent 'Processing your request...' message to user.")
        
        reply_message = chatgpt.submit(update.message.text)
        logging.info(f"Received reply from chatgpt.submit: {reply_message}")
        
        if reply_message.startswith('Error:'):
            context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
        else:
            context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=processing_message.message_id,
                text=reply_message
            )
    except Exception as e:
        logging.error(f"An exception occurred in equiped_chatgpt: {e}")
        context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred while processing your request.")

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')

def add(update: Update, context: CallbackContext) -> None:
    """Increments the counter for a given keyword."""
    try:
        if context.args:
            keyword = context.args[0]
            new_value = redis1.incr(keyword)
            update.message.reply_text(f"You have mentioned '{keyword}' {new_value} times.")
            logging.info(f"Incremented keyword '{keyword}' by 1. New value is {new_value}.")
        else:
            update.message.reply_text("Usage: /add <keyword>")
    except Exception as e:
        update.message.reply_text("An error occurred while processing your request.")
        logging.error(f"Error in /add command: {e}")

def hello(update: Update, context: CallbackContext) -> None:
    """Reply with 'Good day, <name>!' when the command /hello is issued."""
    try:
        name = ' '.join(context.args)
        if name:
            update.message.reply_text(f'Good day, {name}!')
            logging.info(f"User {update.effective_user.first_name} said hello to {name}.")
        else:
            update.message.reply_text('Good day!')
            logging.info(f"User {update.effective_user.first_name} saßid hello.")
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /hello <name>')
        logging.error("Error in /hello: missing or invalid arguments.")

def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message back to them in uppercase."""
    try:
        message_to_echo = ' '.join(context.args).upper() if context.args else 'You did not provide any text to echo.'
        update.message.reply_text(message_to_echo)
        user = update.effective_user.first_name if update.effective_user.first_name else "Unknown user"
        logging.info(f"User {user} requested echo with message: {' '.join(context.args)}. Echoed back: {message_to_echo}.")
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /echo <text to echo>')
        logging.error("Error in /echo: missing or invalid arguments.")

if __name__ == '__main__':
    main()