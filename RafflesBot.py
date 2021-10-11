from time import sleep
from requests import get
from instabot import Bot
import telebot
from telebot import types

botP = Bot()
sleep(5)
#-------------------------SETTINGS-------------------------
botP.login(username = "USERNAME",  password = "PASSWORD", use_cookie = False)
bot = telebot.TeleBot('TELEGRAM BOT TOKEN');
#----------------------------------------------------------

#-------------------------FUNCTIONS------------------------
def is_admin(user_id):
    with open('admins.txt') as f:
        strings = f.read()
        return True if user_id in strings else False
def is_repeat(post_ident):
    with open('ids.txt') as f:
        strings = f.read()
        return True if post_ident in strings else False

def parsing(profile):
    twony_last_medias = botP.get_user_medias(profile, filtration = None)
    media_id = twony_last_medias[0]
    media_info = botP.get_media_info(media_id)[0]
    try:
        img = str(media_info['carousel_media'][0]['image_versions2']['candidates'][0]['url'])
    except:
        img = 'https://i.imgur.com/VIdVLZd.jpeg'
    text = str(media_info['caption']['text'])
    post_id = str(media_info['id'])
    return img, text, post_id

def subscribe(mes):
    file = open('insts.txt', "r")
    insts = []
    is_empty = False
    while True:
        line = file.readline()
        if not line:
            break
        insts.insert(0, line.strip()[:-1])
    if len(insts) == 0:
        error_msg = '❌' + ' list of accounts is empty'
        bot.send_message(mes.from_user.id, error_msg)
        is_empty = True
    if is_empty == False:
        for j in range (len(insts)):
            image, text, post_id = parsing(insts[j])
            if not is_repeat(post_id + ';'):
                strings = open('ids.txt').read()
                if not(post_id in strings):
                    with open('ids.txt', 'a') as file:
                        file.write('\n' + post_id + ';')
                    print("New post: " + post_id)
                    if text.lower().find('раффл') !=-1 or text.lower().find('рафл') !=-1 or text.lower().find('raffle') !=-1 or text.lower().find('регистрация') !=-1:
                        success_msg = '✔️' + ' instagram.com/' + insts[j] + '\n' + text
                        bot.send_photo(mes.from_user.id, get(image).content, caption = success_msg)
#----------------------------------------------------------

#--------------------------SCRIPT--------------------------
is_sub = False
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":
        f = open('insts.txt', 'w')
        f.close()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="✅ The list of accounts has been cleared!", reply_markup=None)
    elif call.data == "no":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="The request has been canceled!", reply_markup=None)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/start":
        bot.send_message(message.from_user.id, "Hi! I am a bot that sends you a notification about new raffles of sneakers! My creator: @larrriiin\nCommands - /help")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "/check - check all last posts from sources at once\n/add - add new sources (for admin only)\n/clear - delete all sources (for admin only)\n/list - view all sources\n/sub - subscribe to the newsletter of new raffles")
    elif message.text == "/check":
        file = open('insts.txt', "r")
        insts = []
        is_empty = False
        while True:
            line = file.readline()
            if not line:
                break
            insts.insert(0, line.strip()[:-1])
        if len(insts) == 0:
            error_msg = '❌' + ' list of accounts is empty'
            bot.send_message(message.from_user.id, error_msg)
            is_empty = True
        if is_empty == False:
            for j in range (len(insts)):
                image, text, post_id = parsing(insts[j])
                strings = open('ids.txt').read()
                if not(post_id in strings):
                    with open('ids.txt', 'a') as file:
                        file.write('\n' + post_id + ';')
                if text.lower().find('раффл') !=-1 or text.lower().find('рафл') !=-1 or text.lower().find('raffle') !=-1 or text.lower().find('регистрация') !=-1:
                    success_msg = '✔️' + ' instagram.com/' + insts[j] + '\n' + text
                    bot.send_photo(message.chat.id, get(image).content, caption = success_msg)
                else:
                    error_msg = '❌' + ' instagram.com/' + insts[j] + ' THE LAST POST IS NOT A RAFFLE'
                    bot.send_message(message.from_user.id, error_msg)
    elif message.text == "/add":
        if is_admin(str(message.from_user.id) + ';'):
            bot.send_message(message.from_user.id, '✅ Enter /add and a nickname from instagram (without @, example: /add larrriiin)')
        else:
            bot.send_message(message.from_user.id, '🛑 Access is denied')
    elif "/add" in message.text and len(str(message.text))>5:
        if is_admin(str(message.from_user.id) + ';'):
            inst = message.text[5:]
            if botP.get_user_id_from_username(inst) != None:
                strings = open('insts.txt').read()
                if inst in strings:
                    print('Already added')
                    bot.send_message(message.from_user.id, '🛑 The account is already in the list for checking!')
                else:
                    if len(strings)!=0:
                        with open('insts.txt', 'a') as file:
                            file.write('\n' + inst + ';')
                    else:
                        with open('insts.txt', 'a') as file:
                            file.write(inst + ';')
                    print('ADDED!')
                    bot.send_message(message.from_user.id, '✅ Successfully added!')
            else:
                bot.send_message(message.from_user.id, '🛑 There is no user with this nickname')
        else:
            bot.send_message(message.from_user.id, '🛑 Access is denied')
    elif message.text == "/clear":
        if is_admin(str(message.from_user.id) + ';') == True:
            keyboard = types.InlineKeyboardMarkup();
            key_yes = types.InlineKeyboardButton(text='Yes', callback_data='yes');
            keyboard.add(key_yes);
            key_no= types.InlineKeyboardButton(text='No', callback_data='no');
            keyboard.add(key_no);
            flag = None
            bot.send_message(message.from_user.id, text='❗️ Are you sure you want to clear the list of accounts for parsing?', reply_markup=keyboard)
        else:
            bot.send_message(message.from_user.id, '🛑 Access is denied')

    elif message.text == "/list":
        file = open('insts.txt', "r")
        insts = []
        success_msg = ""
        is_empty = False
        while True:
            line = file.readline()
            if not line:
                break
            insts.insert(0, line.strip()[:-1])
        if len(insts) == 0:
            error_msg = '❌' + ' list of accounts is empty'
            bot.send_message(message.from_user.id, error_msg)
            is_empty = True
        if is_empty == False:
            for i in range (len(insts)):
                image, text, post_id = parsing(insts[i])
                strings = open('ids.txt').read()
                if not(post_id in strings):
                    with open('ids.txt', 'a') as file:
                        file.write('\n' + post_id + ';')
                if text.lower().find('раффл') !=-1 or text.lower().find('рафл') !=-1 or text.lower().find('raffle') !=-1 or text.lower().find('регистрация') !=-1:
                    success_msg = success_msg + '✔️' + ' instagram.com/' + insts[i] + '\n'
                else:
                    success_msg = success_msg + '❌' + ' instagram.com/' + insts[i] + '\n'
            bot.send_message(message.from_user.id, success_msg)
    elif message.text == "/sub":
        global is_sub
        flag = 0
        if is_sub == False:
            is_sub = True
        else:
            is_sub = False
        if is_sub == True:
            while is_sub == True:
                subscribe(message)
                sleep(5)
                flag = 0
        else:
            if flag == 0:
                bot.send_message(message.from_user.id, '✔️ You have successfully unsubscribed!')
                flag = 1
    elif message.text == "/id":
        bot.send_message(message.from_user.id, message.from_user.id)
bot.polling(none_stop=True, interval=0)
#----------------------------------------------------------