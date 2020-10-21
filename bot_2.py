import telebot
from telebot import types
import os
import avito
import time
from bot_db import SQLiteDB


BOT_TOKEN = '1342572499:AAHYwYKXbrCB3Pmy2Rf9eJrsK63e73kA3_c'
DB = SQLiteDB("db.sqlite")
bot = telebot.TeleBot(BOT_TOKEN)
hideBoard = types.ReplyKeyboardRemove()



@bot.message_handler(commands=["start"])
def start_bot(message, start = True):
    DB.new_chat_add(message.chat.id, start)
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Начать поиск", callback_data="find")
    callback_button2 = types.InlineKeyboardButton(text="Просмотреть ваши ссылки", callback_data="urls")
    callback_button3 = types.InlineKeyboardButton(text="Добавить новую ссылку", callback_data="add_url")
    keyboard.add(callback_button)
    keyboard.add(callback_button2)
    keyboard.add(callback_button3)
    avito_jpg = open('avito.jpg', 'rb')
    bot.send_photo(message.chat.id, avito_jpg, 
    """Привет. Я могу присылать тебе новые объявления с авито! 
    Для работы с ботом воспользуйтесь кнопками под сообщением. 
    Добавьте ссылку на поиск и нажмите <Начать поиск> """, 
                    reply_markup = keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_button(call):
    if call.message:
        if call.data == "find":
            find_messages(call.message)
        elif call.data == "urls":
            send_urls(call.message)
        elif call.data == "start":
            start_bot(call.message)
        elif "delete" in call.data:
            hash_id = call.data[call.data.index('_')+1:]
            DB.delete_url(id = hash_id)
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        elif "add_url" in call.data:
            bot.send_message(call.message.chat.id, 'Отправь мне ссылку на поиск Авито, например: https://www.avito.ru/moskva?metro=1')

            

@bot.message_handler(commands=["stop"])
def stop_send(message):
    DB.disable_bot(message.chat.id)
    bot.send_message(message.chat.id, 'Прекращаю отслеживать новые объявления.', reply_markup = hideBoard)
    start_bot(message, False)



@bot.message_handler(commands=["find"])
def find_messages(message):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True)
    keyboard.add("Остановить поиск")

    DB.enable_bot(message.chat.id)
    urls = DB.get_urls(message.chat.id)
    old_links = {}
    for url in urls:
        time.sleep(3)
        page = avito.connect_url(url)
        if page == 0:
            bot.send_message(message.chat.id, f'Cсылка {url} не рабочая! Удалите её из поиска.')
        else: 
            links = avito.parse_page(page)
            old_links[url] = links
                       
    while(True):
        time.sleep(5)
        for url in urls:
            page = avito.connect_url(url)
            if page == 0:
                bot.send_message(message.chat.id, f'Cсылка {url} не рабочая! Удалите её из поиска.')
            else: 
                links = avito.parse_page(page)
                for link in links:
                    if link not in old_links[url]:
                        old_links[url].append(link)
                        if DB.check_bot(message.chat.id):
                            bot.send_message(message.chat.id, link, reply_markup = keyboard)
                        else:
                            return
                if len(old_links[url]) > 50:
                    old_links[url] = old_links[url][:40]
        


@bot.message_handler(commands=["urls"])
def send_urls(message):
    urls = DB.get_urls(message.chat.id)
    if urls:
        for url in urls:
            callback_button = types.InlineKeyboardButton(text="Удалить", callback_data="delete_"+ DB.get_url_hash(message.chat.id, url))
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(callback_button)
            bot.send_message(message.chat.id, {url}, reply_markup=keyboard)
    else:
        keyboard = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text="Добавить новую ссылку", callback_data="add_url")
        keyboard.add(callback_button)
        bot.send_message(message.chat.id, "Вы ещё не добавили ссылки для отслеживания!", reply_markup=keyboard)

@bot.message_handler(regexp ="https:\/\/www.avito.ru\/", content_types=['text'])
def check_answer(message):
    print(message.chat.id)
    URL = message.text.replace('www','m')
    page = avito.connect_url(URL)
    print (page)
    if page == 0:
        bot.send_message(message.chat.id, 'Говно ссылку прислал! Попробуй ещё раз!')
    else: 
        DB.new_url_add(message.chat.id, URL)
        bot.send_message(message.chat.id, 'Буду присылать тебе новые объявления из этого поиска.')

@bot.message_handler(regexp ="Остановить поиск", content_types=['text'])
def stop_finding(message):
    stop_send(message)

if __name__ == '__main__':
# Функция infinity_polling запускает т.н. Long Polling, бот должен стараться не прекращать работу 
# при возникновении каких-либо ошибок. При этом, само собой, за ботом нужно следить, ибо сервера 
# Telegram периодически перестают отвечать на запросы или делают это с большой задержкой приводя к ошибкам 5xx)
    bot.infinity_polling()


    
