import os
import telegram
import requests
import json
import firebase_admin
from firebase_admin import credentials, firestore
from packages import track
from packages.time_helper import Time
from packages.url_validator import *
from packages.pin_validator import *

FIREBASE_PROJECT_ID = os.environ["FIREBASE_PROJECT_ID"]
BOT_TOKEN = os.environ["TELEGRAM_TOKEN"]
SEND_URL = os.environ["SEND_URL"]
HISTORY_URL = os.environ["HISTORY_URL"]
ADMIN_TOKEN = os.environ["ADMIN_TOKEN"]

TAG = "main.py"
UPDATE_1 = "CALLBACK"
UPDATE_2 = "MESSAGE"
SUCCESSFUL = "PASSED"
FAILED = "ERROR"

#firebase init
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': FIREBASE_PROJECT_ID,
})

db = firestore.client()

Time = Time()

def webhook(request):
    print(TAG, "Request received!")

    bot = telegram.Bot(token=BOT_TOKEN)

    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        if update == None:
            print(TAG, FAILED, "Update == NONE")
            return

        callbackQuery = update.callback_query
        
        if callbackQuery != None:
            query = callbackQuery.data
            chatID = callbackQuery.message.chat_id

            print(TAG, UPDATE_1, chatID, callbackQuery.message.from_user.first_name, query)
            
            if query == "PIN":
                bot.sendMessage(chat_id=chatID, 
                                text="Please enter your 4-digit PIN",
                                disable_notification=True)
                query_ref = db.collection("querying").document("replies")
                query_ref.set({
                    str(chatID): "setpin " + Time.getDateTime()
                }, merge=True)
                print(TAG, UPDATE_1, query, SUCCESSFUL)
            elif query == "URL":
                bot.sendMessage(chat_id=chatID, 
                                text="Please enter your URL\n\nE.g: https://temptaking.ado.sg/group/<uniqueCode>",
                                disable_notification=True)
                query_ref = db.collection("querying").document("replies")
                query_ref.set({
                    str(chatID): "seturl " + Time.getDateTime()
                }, merge=True)
                print(TAG, UPDATE_1, query, SUCCESSFUL)
            elif query == "SENDER":
                bot.sendChatAction(chat_id=chatID, action=telegram.ChatAction.TYPING)

                cr_details_dict = db.collection("chatrooms").document(str(chatID)).get().to_dict()
                doesURLexist = "sendurl" in cr_details_dict
                
                if doesURLexist:
                    reply_markup = getMemberNamesKeyboardMarkup(cr_details_dict["sendurl"])

                    query_ref = db.collection("querying").document("replies")
                    
                    query_ref.set({
                        str(chatID): "setsender " + Time.getDateTime()
                    }, merge=True)

                    bot.sendMessage(chat_id=chatID, 
                                    text="👾 Please select your name below", 
                                    reply_markup=reply_markup,
                                    disable_notification=True)
                else:
                    bot.sendMessage(chat_id=chatID, 
                                    text="⚠ URL required to set sender!\n\n/url to set url",
                                    disable_notification=True)
                print(TAG, UPDATE_1, query, SUCCESSFUL)
            elif query == "TRACKURL":
                bot.sendMessage(chat_id=chatID, 
                                text="Please enter the tracking URL\n\nE.g: https://temptaking.ado.sg/overview/<uniqueCode>",
                                disable_notification=True)
                query_ref = db.collection("querying").document("replies")
                query_ref.set({
                    str(chatID): "settrackurl " + Time.getDateTime()
                }, merge=True)
                print(TAG, UPDATE_1, query, SUCCESSFUL)
            return

        if update.message == None or update.message.text == None:
            print(TAG, FAILED, "Message == None")
            return

        message = update.message.text
        chatID = update.message.chat_id
        
        print(TAG, UPDATE_2, str(chatID), update.message.from_user.first_name, message)

        if message.startswith("/"):
            cr_ref = db.collection("chatrooms").document(str(chatID))
            cr_details = cr_ref.get()

            if not cr_details.exists:
                cr_ref.set({
                        "groupType": update.message.chat.type,
                        "groupTitle": update.message.chat.title,
                        "first_name": update.message.chat.first_name,
                })
            
            if message.startswith("/start"):
                bot.sendChatAction(chat_id=chatID, action=telegram.ChatAction.TYPING)

                welcomeMessage = "🌟 Welcome to TempAdoBot\! 🌟\n\n" + \
                                    "__With me, you can__\n" + \
                                    "🏹 get daily reminders for temperature submissions\n" + \
                                    "🏹 send temperatures directly\n" + \
                                    "🏹 check your temperature records for the day\n" + \
                                    "🏹 check who have not send their temperatures\n\n" + \
                                    "/setup to start sending temperatures\n" + \
                                    "/help for all available commands"
                bot.sendMessage(chat_id=chatID,
                                text=welcomeMessage,
                                parse_mode=telegram.ParseMode.MARKDOWN_V2,
                                disable_notification=True)
            elif message.startswith("/help"):
                bot.sendChatAction(chat_id=chatID, action=telegram.ChatAction.TYPING)

                header = "✋ *TempAdoBot Help Page* ✋\n\n"
                commands = "/help \- help page for this bot\n\n" + \
                            "📣 If you are new:\n" + \
                            "/setup \- a one\-time setup to upload temperatures\n\n" + \
                            "📣 Uploading of temperature records:\n" + \
                            "/pin \- change your pin\n" + \
                            "/url \- change your url\n" + \
                            "/sender \- change who you are \n" + \
                            "/history \- view temperature submissions for today\n" + \
                            "/sendtemp \- send your temperature\n\n" + \
                            "📣 Tracking of everyone\'s temperature records \(For commanders\?\):\n" + \
                            "/track \- see who have yet to upload their temperatures\n\n" + \
                            "💡 Subscribing to reminders:\n" + \
                            "/subscribe \- get daily reminders at 1100 and 1530\n" + \
                            "/unsubscribe \- unsubscribe to daily reminders"       
                text = header + commands
                bot.sendMessage(chat_id=chatID, 
                                text=text, 
                                parse_mode=telegram.ParseMode.MARKDOWN_V2,
                                disable_notification=True)
            elif message.startswith("/setup"):
                bot.sendChatAction(chat_id=chatID, action=telegram.ChatAction.TYPING)

                messageText = "__Getting started__\n\n" + \
                                "1️⃣ Setup your PIN\n" + \
                                "2️⃣ Setup you URL\n" + \
                                "3️⃣ Setup your identity\n" + \
                                "4️⃣ Start sending your temperatures\!"

                button_list = [
                        [telegram.InlineKeyboardButton("🔑 Set PIN", callback_data="PIN"),
                        telegram.InlineKeyboardButton("🌐 Set URL", callback_data="URL")],
                        [telegram.InlineKeyboardButton("🙆‍♂️ Set sender", callback_data="SENDER")]
                ]

                reply_markup = telegram.InlineKeyboardMarkup(button_list)
                bot.sendMessage(chat_id=chatID, 
                                text=messageText,
                                reply_markup=reply_markup,
                                parse_mode=telegram.ParseMode.MARKDOWN_V2,
                                disable_notification=True)
            elif message.startswith("/pin"):
                bot.sendChatAction(chat_id=chatID, action=telegram.ChatAction.TYPING)

                cr_details_dict = cr_details.to_dict()
                doesPINexist = ("sendpin " + str(update.message.from_user.id)) in cr_details_dict

                pin = None
                inlineButtonText = "🔑 Set PIN"
                messageText = "🔒 You have not setup your PIN!"

                if doesPINexist:
                    pin = cr_details_dict["sendpin " + str(update.message.from_user.id)]
                    inlineButtonText = "🔑 Change PIN"
                    messageText = "🔓 Your PIN is: " + pin
                
                button_list = [
                        telegram.InlineKeyboardButton(inlineButtonText, callback_data="PIN")
                ]

                reply_markup = telegram.InlineKeyboardMarkup([button_list])
                bot.sendMessage(chat_id=chatID, 
                                text=messageText,
                                reply_markup=reply_markup,
                                disable_notification=True)
            elif message.startswith("/url"):
                bot.sendChatAction(chat_id=chatID, action=telegram.ChatAction.TYPING)

                cr_details_dict = cr_details.to_dict()
                doesURLexist = "sendurl" in cr_details_dict

                url = None
                inlineButtonText = "🌐 Set URL"
                messageText = "⚠ You have not setup your URL!"

                if doesURLexist:
                    url = cr_details_dict["sendurl"]
                    inlineButtonText = "🌐 Change URL"
                    messageText = "🌏 URL to send temperature records:\n\n" + url

                button_list = [
                        telegram.InlineKeyboardButton(inlineButtonText, callback_data="URL")
                ]

                reply_markup = telegram.InlineKeyboardMarkup([button_list])
                bot.sendMessage(chat_id=chatID, 
                                text=messageText,
                                reply_markup=reply_markup,
                                disable_notification=True)
            elif message.startswith("/sender"):
                bot.sendChatAction(chat_id=chatID, action=telegram.ChatAction.TYPING)

                cr_details_dict = cr_details.to_dict()
                doesSenderExist = str(update.message.from_user.id) in cr_details_dict

                sender = None
                inlineButtonText = "🙆‍♂️ Set sender"
                messageText = "👻 You have not identified yourself!"

                if doesSenderExist:
                    sender = cr_details_dict[str(update.message.from_user.id)]
                    inlineButtonText = "💁‍♂️ Change sender"
                    messageText = "🧔 " + update.message.from_user.first_name + " is currently bound to " + sender
                
                button_list = [
                        telegram.InlineKeyboardButton(inlineButtonText, callback_data="SENDER")
                ]

                reply_markup = telegram.InlineKeyboardMarkup([button_list])
                bot.sendMessage(chat_id=chatID, 
                                text=messageText,
                                reply_markup=reply_markup,
                                disable_notification=True)
            elif message.startswith("/history"):
                bot.sendChatAction(chat_id=chatID, action=telegram.ChatAction.TYPING)

                cr_details_dict = cr_details.to_dict()
                doesURLexist = "sendurl" in cr_details_dict
                doesPINexist = "sendpin " + str(update.message.from_user.id) in cr_details_dict
                doesSenderExist = str(update.message.from_user.id) in cr_details_dict

                if doesURLexist and doesPINexist and doesSenderExist:
                    URL = cr_details_dict["sendurl"]
                    GROUPCODE = None
                    #temp code to cache groupcodes
                    try: 
                        GROUPCODE = cr_details_dict["groupCode"]
                    except:
                        GROUPCODE = URL[URL.rindex("/") + 1:]
                        cr_ref.set({
                            "groupCode": GROUPCODE
                        }, merge=True)

                    MEMBERNAME = cr_details_dict[str(update.message.from_user.id)]
                    MEMBERID = getMemberIdFromName(URL, MEMBERNAME)
                    PIN = cr_details_dict["sendpin " + str(update.message.from_user.id)]

                    data = {
                        "groupCode": GROUPCODE,
                        "memberId": MEMBERID,
                        "pin": PIN,
                        "startDate": Time.getDate(),
                        "endDate": Time.getDate(),
                        "timezone": Time.TIME_ZONE
                    }

                    try:
                        response = requests.post(url=HISTORY_URL, data=data).text
                        responseDict = json.loads(response)[0]
                        latestAM = responseDict["latestAM"]
                        latestPM = responseDict["latestPM"]

                        if latestAM == "":
                            latestAM = "NO DATA"
                        if latestPM == "":
                            latestPM = "NO DATA"

                        messageText = "☀ AM temperature: " + latestAM + "\n" + \
                                        "🌙 PM temperature: " + latestPM
                    except:
                        messageText = "😢 Looks like temptaking.ado.sg is down. Please try again later!"

                    bot.sendMessage(chat_id=chatID, 
                                    text=messageText,
                                    disable_notification=True)
                else:
                    criteria = getSendTempCriteria(doesURLexist, doesPINexist, doesSenderExist)
                    button_list = getCriteriaFailedInline(doesURLexist, doesPINexist, doesSenderExist)

                    reply_markup = telegram.InlineKeyboardMarkup([button_list])

                    bot.sendMessage(chat_id=chatID, 
                                    text=criteria,
                                    reply_markup=reply_markup,
                                    parse_mode=telegram.ParseMode.MARKDOWN_V2,
                                    disable_notification=True)
            elif message.startswith("/sendtemp"):
                bot.sendChatAction(chat_id=chatID, action=telegram.ChatAction.TYPING)

                cr_details_dict = cr_details.to_dict()
                doesURLexist = "sendurl" in cr_details_dict
                doesPINexist = "sendpin " + str(update.message.from_user.id) in cr_details_dict
                doesSenderExist = str(update.message.from_user.id) in cr_details_dict

                if doesURLexist and doesPINexist and doesSenderExist:
                    reply_markup = getTemperatureKeyboardMarkup()

                    query_ref = db.collection("querying").document("replies")
                    query_ref.set({
                        str(chatID): "sendtemp " + Time.getDateTime()
                    }, merge=True)

                    bot.sendMessage(chat_id=chatID, 
                                    text="📤 Please select your temperature below 📤\n\n__You are reminded to take your temperature first\!__", 
                                    reply_markup=reply_markup,
                                    parse_mode=telegram.ParseMode.MARKDOWN_V2,
                                    disable_notification=True)
                else:
                    criteria = getSendTempCriteria(doesURLexist, doesPINexist, doesSenderExist)
                    button_list = getCriteriaFailedInline(doesURLexist, doesPINexist, doesSenderExist)

                    reply_markup = telegram.InlineKeyboardMarkup([button_list])

                    bot.sendMessage(chat_id=chatID, 
                                    text=criteria,
                                    reply_markup=reply_markup,
                                    parse_mode=telegram.ParseMode.MARKDOWN_V2,
                                    disable_notification=True)
            elif message.startswith("/track"):
                bot.sendChatAction(chat_id=chatID, action=telegram.ChatAction.TYPING)

                cr_details_dict = cr_details.to_dict()
                doesURLexist = "checkurl" in cr_details_dict

                inlineButtonText = "🌐 Set tracking URL"
                messageText = "⚠ You have not setup your URL\!\n\n" + \
                                "A tracking URL is required, which is different from the one used to send temperatures\n\n" + \
                                "Use /history instead to view your temperature history"

                if doesURLexist:
                    inlineButtonText = "🌐 Change tracking URL"
                    data = track.getGroupData(cr_details_dict["checkurl"])
                    messageText = track.formatReminder(data)

                button_list = [
                        telegram.InlineKeyboardButton(inlineButtonText, callback_data="TRACKURL")
                ]

                reply_markup = telegram.InlineKeyboardMarkup([button_list])
                bot.sendMessage(chat_id=chatID, 
                                text=messageText,
                                parse_mode=telegram.ParseMode.MARKDOWN_V2,
                                reply_markup=reply_markup,
                                disable_notification=True)
            elif message.startswith("/subscribe") or message.startswith("/unsubscribe"):
                bot.sendChatAction(chat_id=chatID, action=telegram.ChatAction.TYPING)

                sub_ref = db.collection("subscribers").document("reminderSubscribers")
                sub_details_dict = sub_ref.get().to_dict()

                if message.startswith("/subscribe"):
                    if str(chatID) not in sub_details_dict or not sub_details_dict[str(chatID)]:
                            sub_ref.set({
                                str(chatID): True
                            }, merge=True)
                            bot.sendMessage(chat_id=chatID, 
                                            text="💡 Subscribed!\n\n" + \
                                                    "You will now receive reminders for AM and PM temperatures",
                                            disable_notification=True)
                    else:
                        bot.sendMessage(chat_id=chatID, 
                                        text="💡 You have already subscribed!",
                                        disable_notification=True)
                else:
                    if str(chatID) in sub_details_dict and sub_details_dict[str(chatID)]:
                            sub_ref.set({
                                str(chatID): False
                            }, merge=True)
                            bot.sendMessage(chat_id=chatID, 
                                            text="🍼 Unsubscribed!\n\n" + \
                                                    "You will not receive reminders for AM and PM temperatures",
                                            disable_notification=True)
                    else:
                        bot.sendMessage(chat_id=chatID, 
                                        text="🍼 You have not subscribed!",
                                        disable_notification=True)
            elif message.startswith("/broadcast " + ADMIN_TOKEN):
                header = "__Message from TempAdoBot__"
                body = message.split(" ")[2]
                text = header + "\n\n" + body

                chats = getAllChats()

                for chat in chats:
                    bot.sendMessage(chat_id=254492482,
                                    text=int(chat),
                                    parse_mode=telegram.ParseMode.MARKDOWN_V2)
            else:
                bot.sendMessage(chat_id=chatID, 
                                text="⚠ Invalid command!\n\n/help for a list of available commands",
                                disable_notification=True)
        else:
            query_ref = db.collection("querying").document("replies")
            query_details = query_ref.get()
            if not query_details.exists:
                return
            query_details_dict = query_details.to_dict()
            isBotQuerying = str(chatID) in query_details_dict

            if isBotQuerying:
                cr_ref = db.collection("chatrooms").document(str(chatID))

                queryType = query_details_dict[str(chatID)]

                if queryType.startswith("setsender"):
                    bot.sendChatAction(chat_id=chatID, action=telegram.ChatAction.TYPING)

                    query_ref.update({
                        str(chatID): firestore.DELETE_FIELD
                    })

                    #ensure query time is not too long ago (1 min)
                    if not isQueryValid(Time.getDateTimeObject(queryType[10:])):
                        bot.sendMessage(chat_id=chatID, 
                                    text="⌛ Command /setsender timeout. Please try again",
                                    reply_markup=telegram.ReplyKeyboardRemove(),
                                    disable_notification=True)
                        return
                    
                    #ensure member is valid
                    cr_details = cr_ref.get()
                    cr_details_dict = cr_details.to_dict()
                    doesURLexist = "sendurl" in cr_details_dict
                    doesPINexist = "sendpin " + str(update.message.from_user.id) in cr_details_dict

                    if doesURLexist:
                        URL = cr_details_dict["sendurl"]
                        members = list(map(lambda x: x["identifier"], getMemberCodeData(URL)))
                        if message not in members:
                            bot.sendMessage(chat_id=chatID, 
                                    text="⚠ " + message + " not a valid member! /sender to try again",
                                    reply_markup=telegram.ReplyKeyboardRemove(),
                                    disable_notification=True)
                            return
                        
                    cr_ref.set({
                        str(update.message.from_user.id): message
                    }, merge=True)

                    bot.sendMessage(chat_id=chatID, 
                                    text="🧔 Sender set!\n\n" + update.message.from_user.first_name + " is now bound to " + message,
                                    reply_markup=telegram.ReplyKeyboardRemove(),
                                    disable_notification=True)
                elif queryType.startswith("sendtemp"):
                    bot.sendChatAction(chat_id=chatID, action=telegram.ChatAction.UPLOAD_DOCUMENT)
                    query_ref.update({
                        str(chatID): firestore.DELETE_FIELD
                    })

                    #ensure query time is not too long ago (1 min)
                    if not isQueryValid(Time.getDateTimeObject(queryType[9:])):
                        bot.sendMessage(chat_id=chatID, 
                                    text="⌛ Command timeout. Please try again",
                                    reply_markup=telegram.ReplyKeyboardRemove(),
                                    disable_notification=True)
                        return
                    
                    cr_details = cr_ref.get()
                    cr_details_dict = cr_details.to_dict()
                    doesURLexist = "sendurl" in cr_details_dict
                    doesPINexist = "sendpin " + str(update.message.from_user.id) in cr_details_dict
                    doesMemberexist = str(update.message.from_user.id) in cr_details_dict

                    if doesURLexist and doesPINexist and doesMemberexist:
                        URL = cr_details_dict["sendurl"]
                        MEMBERNAME = cr_details_dict[str(update.message.from_user.id)]
                        MEMBERID = getMemberIdFromName(URL, MEMBERNAME)
                        TEMPERATURE = message
                        PIN = cr_details_dict["sendpin " + str(update.message.from_user.id)]

                        try:
                            reply = sendTemperature(URL, MEMBERID, TEMPERATURE, PIN)
                            if reply == "OK":
                                bot.sendMessage(chat_id=chatID, 
                                                text="🌡 Temperature sent!\n\n",
                                                reply_markup=telegram.ReplyKeyboardRemove(),
                                                disable_notification=True)
                            elif "Wrong pin" in reply:
                                bot.sendMessage(chat_id=chatID,
                                            text="⚠ PIN inputted was wrong!\n\n/pin to reset pin!",
                                            reply_markup=telegram.ReplyKeyboardRemove(),
                                            disable_notification=True)
                        except :
                            bot.sendMessage(chat_id=chatID,
                                            text="⚠ Temperature failed to send!\n\n/sendtemp to try again!",
                                            reply_markup=telegram.ReplyKeyboardRemove(),
                                            disable_notification=True)
                            print(TAG, FAILED, "sendtemp")
                    else:
                        criteria = getSendTempCriteria(doesURLexist, doesPINexist, doesMemberexist)
                        bot.sendMessage(chat_id=chatID,
                                        text=criteria,
                                        parse_mode=telegram.ParseMode.MARKDOWN_V2,
                                        disable_notification=True)
                elif queryType.startswith("setpin"):
                    bot.sendChatAction(chat_id=chatID, action=telegram.ChatAction.UPLOAD_DOCUMENT)

                    query_ref.update({
                        str(chatID): firestore.DELETE_FIELD
                    })

                    #ensure query time is not too long ago (1 min)
                    if not isQueryValid(Time.getDateTimeObject(queryType[7:])):
                        bot.sendMessage(chat_id=chatID, 
                                    text="⌛ Command timeout. Please try again",
                                    disable_notification=True)
                        return

                    pin = message

                    try:
                        if isSendPINValid(pin):
                            cr_ref.set({
                                "sendpin " + str(update.message.from_user.id): pin
                            }, merge=True)
                            bot.sendMessage(chat_id=chatID, 
                                            text="✅ " + update.message.from_user.first_name + "'s PIN set as: " + pin + "\n\n/pin to retrieve PIN",
                                            disable_notification=True)
                        else:
                            bot.sendMessage(chat_id=chatID, 
                                            text="⚠ Invalid PIN!\n\nPINs are 4-digit numbers! Eg: 0000",
                                            disable_notification=True)
                    except (PINLengthError, ValueError) as e:
                        print("[main.py] webhook: /pin -- " + str(e))
                        bot.sendMessage(chat_id=chatID, 
                                            text="⚠ Invalid PIN!\n\nPINs are 4-digit numbers! Eg: 0000",
                                            disable_notification=True)
                elif queryType.startswith("seturl"):
                    bot.sendChatAction(chat_id=chatID, action=telegram.ChatAction.UPLOAD_DOCUMENT)

                    query_ref.update({
                        str(chatID): firestore.DELETE_FIELD
                    })

                    #ensure query time is not too long ago (1 min)
                    if not isQueryValid(Time.getDateTimeObject(queryType[7:])):
                        bot.sendMessage(chat_id=chatID, 
                                        text="⌛ Command timeout. Please try again",
                                        disable_notification=True)
                        return

                    url = message
                    groupCode = url[url.rindex("/") + 1:]

                    try:
                        if isSendURLValid(url):
                            cr_ref.set({
                                "sendurl": url,
                                "groupCode": groupCode
                            }, merge=True)
                            bot.sendMessage(chat_id=chatID, 
                                            text="✅ URL set as:\n\n" + url,
                                            disable_notification=True)
                        else:
                            bot.sendMessage(chat_id=chatID, 
                                            text="⚠ Invalid URL!\n\nURL Example: https://temptaking.ado.sg/group/<uniqueCode>",
                                            disable_notification=True)
                    except (MissingPrefixError, InvalidURLError, InvalidCodeError) as e:
                        print("[main.py] webhook: /setcheckurl -- " + str(e))
                        bot.sendMessage(chat_id=chatID, 
                                        text="⚠ " + str(e),
                                        disable_notification=True)
                    except:
                        print("[main.py] webhook: /setcheckurl -- Unknown Error occurred")
                        bot.sendMessage(chat_id=chatID, 
                                        text="⚠ Invalid URL!\n\nURL Example: https://temptaking.ado.sg/group/<uniqueCode>",
                                        disable_notification=True)
                elif queryType.startswith("settrackurl"):
                    bot.sendChatAction(chat_id=chatID, action=telegram.ChatAction.UPLOAD_DOCUMENT)

                    query_ref.update({
                        str(chatID): firestore.DELETE_FIELD
                    })

                    #ensure query time is not too long ago (1 min)
                    if not isQueryValid(Time.getDateTimeObject(queryType[12:])):
                        bot.sendMessage(chat_id=chatID, 
                                        text="⌛ Command timeout. Please try again",
                                        disable_notification=True)
                        return

                    url = message

                    try:
                        if isCheckURLValid(url):
                            cr_ref.set({
                                "checkurl": url
                            }, merge=True)
                            bot.sendMessage(chat_id=chatID, 
                                            text="✅ Tracking URL set as:\n\n" + url,
                                            disable_notification=True)
                        else:
                            bot.sendMessage(chat_id=chatID, 
                                            text="⚠ Invalid URL!\n\nURL Example: https://temptaking.ado.sg/overview/<uniqueCode>",
                                            disable_notification=True)
                    except (MissingPrefixError, InvalidURLError) as e:
                        print("[main.py] webhook: /setcheckurl -- " + str(e))
                        bot.sendMessage(chat_id=chatID, 
                                        text="⚠ " + str(e),
                                        disable_notification=True)
                    except:
                        print("[main.py] webhook: /setcheckurl -- Unknown Error occurred")
                        bot.sendMessage(chat_id=chatID, 
                                        text="⚠ Invalid URL!\n\nURL Example: https://temptaking.ado.sg/group/<uniqueCode>",
                                        disable_notification=True)
    return "ok"

def getMemberCodeData(url):
    request = requests.get(url=url)
    text = request.text

    indexStart = text.index("loadContents") + 14
    indexEnd = text.rindex("true") + 7
    data = text[indexStart:indexEnd]
    dataJSON = json.loads(data)

    memberJSON = dataJSON["members"]

    return memberJSON

def getMemberIdFromName(url, name):
    memberJSON = getMemberCodeData(url)
    memberData = tuple(filter(lambda x: x["identifier"] == name, memberJSON))
    memberId = memberData[0]["id"]

    return memberId

def getMemberNamesKeyboardMarkup(url):
    members = list(map(lambda x: [x["identifier"]], getMemberCodeData(url)))
    memberKeyboard = members
    reply_markup = telegram.ReplyKeyboardMarkup(memberKeyboard)
    return reply_markup

def getTemperatureKeyboardMarkup():
    temperatures = [[str(x / 10), str((x + 1) / 10), str((x + 2) / 10)] for x in range(355, 376, 3)]
    return telegram.ReplyKeyboardMarkup(temperatures)

def sendTemperature(url, memberId, temperature, pin):
    GROUPCODE = url[url.rindex("/") + 1:]
    DATE = Time.getDate()
    MERIDIES = Time.getMeridiesFromTime(Time.getTime())

    PAYLOAD = {"groupCode": GROUPCODE,
                "date": DATE,
                "meridies": MERIDIES,
                "memberId": memberId,
                "temperature": temperature,
                "pin": pin}

    request = requests.post(url=SEND_URL, data=PAYLOAD)
    return request.text

def isQueryValid(queryTime):
    timeNow = Time.getDateTimeObject(Time.getDateTime())

    try:
        delta = timeNow - queryTime
        if delta.total_seconds() / 60 < 1:
            return True
        else:
            return False
    except:
        print(TAG, FAILED, "isQueryValid()")
        return False

def getSendTempCriteria(doesURLexist, doesPINexist, doesSenderExist):
    criteriaText = {"PIN": "✔\n\n" if doesPINexist else "⚠ PIN not set\!\n\n",
                "URL": "✔\n\n" if doesURLexist else "⚠ URL not set\!\n\n",
                "Sender": "✔" if doesSenderExist else "⚠ Sender not set\!"}
    criteria = ""
    for x in criteriaText:
        criteria += (x + ": " + criteriaText[x])
    return criteria

def getCriteriaFailedInline(doesURLexist, doesPINexist, doesSenderExist):
    button_list = []
    if not doesURLexist:
        button_list.append(telegram.InlineKeyboardButton("🌐 Set URL", callback_data="URL"))
    if not doesPINexist:
        button_list.append(telegram.InlineKeyboardButton("🔑 Set PIN", callback_data="PIN"))
    if not doesSenderExist:
        button_list.append(telegram.InlineKeyboardButton("🙆‍♂️ Set sender", callback_data="SENDER"))
    return button_list

def getAllChats():
    allChats = db.collection("chatrooms").stream()
    chatIDs = []
    for chat in allChats:
        chatIDs.append(chat.id)
    
    return chatIDs

print("-----> V1.2.2 Deployment success! <-----")