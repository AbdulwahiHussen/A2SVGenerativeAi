import logging
import os
import openai
from telegram import (
    Message,
    ChatAction,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    Updater,
)
from telegram import Bot
import file_handler
from dotenv import load_dotenv
import json

load_dotenv()

question_format = {
    "JS": [
        {
            "id": 1,
            "question": "Question number 1",
            "options": ["option a", "option b", "option c", "option d"],
            "answer": "option c",
            "score": 0,
            "status": "",
            "user_answer": "",
            "explanation": "brief explanation",
        },
        {
            "id": 2,
            "question": "Question number 2",
            "options": ["option a", "option b", "option c", "option d"],
            "answer": "option c",
            "score": 0,
            "status": "",
            "user_answer": "",
            "explanation": "brief explanation",
        },
    ]
}

openai.api_key = os.environ.get("OPENAI_API_KEY")


TOKEN = os.environ.get("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

user_data = {}


def help(update: Update, context: CallbackContext):
    update.message.reply_text("Please enter file")


def set_page(update: Update, context: CallbackContext):
    user_message = update.message.text
    if user_message.startswith("/readpdf "):
        pages = user_message[len("/readpdf ") :].split()
        if len(pages) == 2:
            start_page_text = pages[0]
            end_page_text = pages[1]

            global user_data
            try:
                user_data["start_page_text"] = start_page_text
                user_data["end_page_text"] = end_page_text
            except:
                user_data.setdefault("start_page_text", start_page_text)
                user_data.setdefault("end_page_text", end_page_text)

            reply_text = f"start page: {start_page_text}, End page: {end_page_text} receieved and stored"
            context.bot.send_message(chat_id=update.effective_chat.id, text=reply_text)
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Invalid format. please provide start and end page",
            )


def send_request(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="choose difficulty\n easy\n medium\n difficult",
    )
    number_of_questions = 5
    difficulty = update.message.text
    text = file_handler.FileHandler(user_data["file_name"])
    start_page = int(user_data["start_page_text"])
    end_page = int(user_data["end_page_text"])
    text.read_file(spage=start_page, epage=end_page)
    processed_string = text.summerized()

    user_message = f"""generate a quiz contining {number_of_questions} different multiple choice questions with 
    different context containing four choices with {difficulty} difficulty the questions must be returned in 
    the following format {question_format} note the 
    question must be in json format!!! also make sure the explanations must be less than 2 lines important!.
    NOTE only use the following text for the generation of quiz {processed_string}"""
    context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING
    )
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=user_message,
        max_tokens=2000,
        temperature=0.1,
        n=1,
        stop=None,
    )
    bot_response = response.choices[0].text.strip()
    json_start_index = bot_response.find("{'JS':")
    json_text = bot_response[json_start_index:]

    context.bot.send_message(chat_id=update.effective_chat.id, text=json_text)


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Hello There, please enter file so we can change it to qiz for you!"
    )


def Enterfile(update: Update, context: CallbackContext):
    file = update.message.document
    file_recieved = context.bot.get_file(file_id=file.file_id)
    file_id = file.file_id
    file_name = file.file_name
    file_size = file.file_size
    mime_type = file.mime_type

    file_recieved.download(file_name)
    update.message.reply_text("Successs")

    reply_text = f"Recieved file: {file_name}\n File ID: {file_id}\n File size:{file_size}bytes\n MIME type: {mime_type}"
    global user_data
    try:
        user_data["file_name"] = file_name
    except:
        user_data.setdefault("file_name", file_name)

    update.message.reply_text(reply_text)


def set_and_request(update: Update, context: CallbackContext):
    logging.info("Setting and Sending Request started")
    set_page(update=update, context=context)
    logging.info("Setting Page Here")
    send_request(update=update, context=context)
    logging.info("Sent the request")


def register(dispatcher):
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.document & ~Filters.text, Enterfile))
    dispatcher.add_handler(CommandHandler("readpdf", set_and_request))
    dispatcher.add_handler(CommandHandler("help", help))


def main():
    updater = Updater(token=TOKEN)
    register(updater.dispatcher)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()