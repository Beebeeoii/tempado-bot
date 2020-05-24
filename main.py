import os
import telegram
import requests
import json
import firebase_admin
from firebase_admin import credentials, firestore
from pytz import timezone
from datetime import datetime
from supportpackage import track

FIREBASE_PROJECT_ID = os.environ["FIREBASE_PROJECT_ID"]
BOT_TOKEN = os.environ["TELEGRAM_TOKEN"]
SEND_URL = os.environ["SEND_URL"]
TIME_ZONE = os.environ["TIME_ZONE"]
MERIDIES_AM = "AM"
MERIDIES_PM = "PM"

#firebase init
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': FIREBASE_PROJECT_ID,
})

db = firestore.client()

def webhook(request):
    print("Request received!", request)

    bot = telegram.Bot(token=BOT_TOKEN)

    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        if update == None or update.message == None or update.message.text == None:
            print("Error: Update or Message == None")
            return

        chatID = update.message.chat_id
        message = update.message.text
        
        print(str(chatID), update.message.from_user.username, message)

        if message.startswith("/"):
            cr_ref = db.collection("chatrooms").document(str(chatID))
            cr_details = cr_ref.get()

            if not cr_details.exists:
                cr_ref.set({
                        "groupType": update.message.chat.type,
                        "groupTitle": update.message.chat.title,
                        "username": update.message.chat.username,
                        "first_name": update.message.chat.first_name,
                        "last_name": update.message.chat.last_name
                })
            
            if message.startswith("/start"):
                welcomeMessage = "🌟 Welcome to TempAdoBot\! 🌟\n\n" + \
                                    "__With me, you can__\n" + \
                                    "🏹 get reminded to submit your AM and PM temperatures daily\n" + \
                                    "🏹 send your temperatures directly through me\n" + \
                                    "🏹 check who have not send their temperatures\n\n" + \
                                    "*It is your responsibility to take your temperatures diligently before sending*\n\n" + \
                                    "/help for all available commands"
                bot.sendMessage(chat_id=chatID,
                                text=welcomeMessage,
                                parse_mode=telegram.ParseMode.MARKDOWN_V2,
                                disable_notification=True)
            elif message.startswith("/setcheckurl"):
                messageSplit = message.split(" ")
                if len(messageSplit) != 2:
                    bot.sendMessage(chat_id=chatID, 
                                    text="⚠ Invalid Syntax!\n\nSyntax: /setcheckurl <url>",
                                    disable_notification=True)
                else:
                    url = messageSplit[1]
                    if isCheckURLValid(url):
                        cr_ref.set({
                            "checkurl": url
                        }, merge=True)
                        bot.sendMessage(chat_id=chatID, 
                                        text="✅ URL set as:\n\n" + url + "\n\n/getcheckurl to retrieve url",
                                        disable_notification=True)
                    else:
                        bot.sendMessage(chat_id=chatID, 
                                        text="⚠ Invalid URL!\n\nURL Example: temptaking.ado.sg/overview/<uniqueCode>",
                                        disable_notification=True)
            elif message.startswith("/getcheckurl"):
                cr_details_dict = cr_details.to_dict()
                doesURLexist = "checkurl" in cr_details_dict
                if doesURLexist:
                    url = cr_details_dict["checkurl"]
                    bot.sendMessage(chat_id=chatID, 
                                    text="😺 URL to check temperature records:\n\n" + url,
                                    disable_notification=True)
                else:
                    bot.sendMessage(chat_id=chatID, 
                                    text="⚠ URL not found!\n\n/setcheckurl to set url",
                                    disable_notification=True)
            elif message.startswith("/forcecheck"):
                cr_details_dict = cr_details.to_dict()
                doesURLexist = "checkurl" in cr_details_dict
                
                if doesURLexist:
                    data = track.getGroupData(cr_details_dict["checkurl"])
                    text = track.formatReminder(data)
                    bot.sendMessage(chat_id=chatID, 
                                    text=text, 
                                    parse_mode=telegram.ParseMode.MARKDOWN_V2,
                                    disable_notification=True)
                else:
                    bot.sendMessage(chat_id=chatID, 
                                    text="⚠ URL not found!\n\n/setcheckurl to set url",
                                    disable_notification=True)
            elif message.startswith("/setsendurl"):
                messageSplit = message.split(" ")
                if len(messageSplit) != 2:
                    bot.sendMessage(chat_id=chatID, 
                                    text="⚠ Invalid Syntax!\n\nSyntax: /setsendurl <url>",
                                    disable_notification=True)
                else:
                    url = messageSplit[1]
                    if isSendURLValid(url):
                        cr_ref.set({
                            "sendurl": url
                        }, merge=True)
                        bot.sendMessage(chat_id=chatID, 
                                        text="✅ URL set as:\n\n" + url + "\n\n/getsendurl to retrieve url",
                                        disable_notification=True)
                    else:
                        bot.sendMessage(chat_id=chatID, 
                                        text="⚠ Invalid URL!\n\nURL Example: temptaking.ado.sg/group/<uniqueCode>",
                                        disable_notification=True)
            elif message.startswith("/getsendurl"):
                cr_details_dict = cr_details.to_dict()
                doesURLexist = "sendurl" in cr_details_dict
                if doesURLexist:
                    url = cr_details_dict["sendurl"]
                    bot.sendMessage(chat_id=chatID, 
                                    text="😺 URL to send temperature records:\n\n" + url,
                                    disable_notification=True)
                else:
                    bot.sendMessage(chat_id=chatID, 
                                    text="⚠ URL not found!\n\n/setsendurl to set url",
                                    disable_notification=True)
            elif message.startswith("/setsendpin"):
                messageSplit = message.split(" ")
                
                if len(messageSplit) != 2:
                    bot.sendMessage(chat_id=chatID, 
                                    text="⚠ Invalid Syntax!\n\nSyntax: /setsendpin <4-digit PIN>",
                                    disable_notification=True)
                else:
                    pin = messageSplit[1]
                    if isSendPINValid(pin):
                        cr_ref.set({
                            "sendpin " + str(update.message.from_user.id): pin
                        }, merge=True)
                        bot.sendMessage(chat_id=chatID, 
                                        text="✅ " + update.message.from_user.first_name + "'s PIN set as: " + pin + "\n\n/getsendpin to retrieve PIN",
                                        disable_notification=True)
                    else:
                        bot.sendMessage(chat_id=chatID, 
                                        text="⚠ Invalid PIN!\n\nPINs are 4-digit numbers! Eg: 0000",
                                        disable_notification=True)
            elif message.startswith("/getsendpin"):
                cr_details_dict = cr_details.to_dict()
                doesPINexist = ("sendpin " + str(update.message.from_user.id)) in cr_details_dict

                if doesPINexist:
                    pin = cr_details_dict["sendpin " + str(update.message.from_user.id)]
                    bot.sendMessage(chat_id=chatID, 
                                    text="🔑 " +  update.message.from_user.first_name + "'s PIN: " + pin,
                                    disable_notification=True)
                else:
                    bot.sendMessage(chat_id=chatID, 
                                    text="⚠" + update.message.from_user.first_name + "'s PIN not found!\n\n/setsendpin to set PIN",
                                    disable_notification=True)
            elif message.startswith("/setsender"):
                cr_details_dict = cr_details.to_dict()
                doesURLexist = "sendurl" in cr_details_dict
                if doesURLexist:
                    reply_markup = getMemberNamesKeyboardMarkup(cr_details_dict["sendurl"])

                    query_ref = db.collection("querying").document("replies")
                    
                    query_ref.set({
                        str(chatID): "setsender " + getDateTime()
                    }, merge=True)

                    bot.sendMessage(chat_id=chatID, 
                                    text="👾 Please select your name below", 
                                    reply_markup=reply_markup,
                                    disable_notification=True)
                else:
                    bot.sendMessage(chat_id=chatID, 
                                    text="⚠ URL required but not found!\n\n/setsendurl to set url",
                                    disable_notification=True)
            elif message.startswith("/help"):
                header = "✋ *TempAdo Telegram Bot Help Page* ✋\n\n"
                title = "List of commands:\n"

                commands = "/help \- help page for this bot\n\n" + \
                            "📣Everything related to *_checking_ temperature records*:\n" + \
                            "/setcheckurl \- sets url to check temperature submissions\n" + \
                            "/getcheckurl \- retrieves url to check temperature submissions, if set\n" + \
                            "/forcecheck \- checks temperature submissions, url must be set beforehand\n\n" + \
                            "📣Everything related to *_sending_ temperature records*:\n" + \
                            "/setsendurl \- sets url to send temperature submissions\n" + \
                            "/getsendurl \- retrives url to send temperature submissions, if set\n" + \
                            "/setsendpin \- sets pin\n" + \
                            "/getsendpin \- retrieves pin, if set\n" + \
                            "/setsender \- sets who you are when you execute /sendtemp\n" + \
                            "/sendtemp \- sends your temperature \(requires sendurl, sendpin and sender to be set\)\n\n" + \
                            "💡 Subscribe to daily AM/PM temperature reminders\n" + \
                            "/subscribe \- subscribes to daily AM and PM temperature reminders at 1100 and 1530 respectively\n" + \
                            "/unsubscribe \- unsubscribes to daily AM and PM temperature reminders"
                            
                text = header + title + commands
                bot.sendMessage(chat_id=chatID, 
                                text=text, 
                                parse_mode=telegram.ParseMode.MARKDOWN_V2,
                                disable_notification=True)
            elif message.startswith("/sendtemp"):
                cr_details_dict = cr_details.to_dict()
                doesURLexist = "sendurl" in cr_details_dict
                doesPINexist = "sendpin " + str(update.message.from_user.id) in cr_details_dict
                doesMemberexist = str(update.message.from_user.id) in cr_details_dict

                if doesURLexist and doesPINexist and doesMemberexist:
                    reply_markup = getTemperatureKeyboardMarkup()

                    query_ref = db.collection("querying").document("replies")
                    query_ref.set({
                        str(chatID): "sendtemp " + getDateTime()
                    }, merge=True)

                    bot.sendMessage(chat_id=chatID, 
                                    text="📤 Please select your temperature below 📤\n\n🛑 __You are reminded to take your temperature first\!__", 
                                    reply_markup=reply_markup,
                                    parse_mode=telegram.ParseMode.MARKDOWN_V2,
                                    disable_notification=True)
                else:
                    criteria = getSendTempCriteria(doesURLexist, doesPINexist, doesMemberexist)
                    bot.sendMessage(chat_id=chatID, 
                                    text=criteria,
                                    parse_mode=telegram.ParseMode.MARKDOWN_V2,
                                    disable_notification=True)
            elif message.startswith("/subscribe") or message.startswith("/unsubscribe"):
                sub_ref = db.collection("subscribers").document("reminderSubscribers")
                sub_details = sub_ref.get()
                sub_details_dict = sub_details.to_dict()

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
                    query_ref.update({
                        str(chatID): firestore.DELETE_FIELD
                    })

                    #ensure query time is not too long ago (1 min)
                    if not isQueryValid(getDateTimeObject(queryType[10:])):
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
                                    text="⚠ " + message + " not a valid member! /setsender to try again",
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
                    query_ref.update({
                        str(chatID): firestore.DELETE_FIELD
                    })

                    #ensure query time is not too long ago (1 min)
                    if not isQueryValid(getDateTimeObject(queryType[9:])):
                        bot.sendMessage(chat_id=chatID, 
                                    text="⌛ Command /sendtemp timeout. Please try again",
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
                                                text="🌡 Temperature sent!\n\n/forcecheck to see who haven't send!",
                                                reply_markup=telegram.ReplyKeyboardRemove(),
                                                disable_notification=True)
                            elif "Wrong pin" in reply:
                                bot.sendMessage(chat_id=chatID,
                                            text="⚠ PIN inputted was wrong!\n\n/setsendpin to reset pin!",
                                            reply_markup=telegram.ReplyKeyboardRemove(),
                                            disable_notification=True)
                        except :
                            bot.sendMessage(chat_id=chatID,
                                            text="⚠ Temperature failed to send!\n\n/sendtemp to try again!",
                                            reply_markup=telegram.ReplyKeyboardRemove(),
                                            disable_notification=True)
                    else:
                        criteria = getSendTempCriteria(doesURLexist, doesPINexist, doesMemberexist)
                        bot.sendMessage(chat_id=chatID,
                                        text=criteria,
                                        parse_mode=telegram.ParseMode.MARKDOWN_V2,
                                        disable_notification=True)
    return "ok"

def isCheckURLValid(url):
    try:
        if track.getGroupData(url) == None:
            return False
        return True
    except:
        return False

def isSendURLValid(url):
    TITLE = "Temperature Recording"
    HEADER = "RECORD YOUR TEMPERATURE"
    INVALID = "Invalid code"

    try:
        request = requests.post(url=url)
        response = request.text
        if INVALID in response:
            return False
        elif TITLE not in response or HEADER not in response:
            return False
        else:
            return True
    except:
        return False

def isSendPINValid(pin):
    try:
        int(pin)
    except:
        return False
    if len(pin) != 4:
        return False

    return True

def getMemberCodeData(url):
    request = requests.post(url=url)
    text = request.text

    indexStart = text.index("loadContents") + 14
    indexEnd = text.rindex("true") + 7
    data = text[indexStart:indexEnd]
    dataJSON = json.loads(data)

#    groupName = dataJSON["groupName"]
#    groupCode = dataJSON["groupCode"]
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
    DATETIME = getDateTime()
    DATE = DATETIME.split(" ")[0]
    TIME = DATETIME.split(" ")[1]
    MERIDIES = getMeridies(TIME)

    PAYLOAD = {"groupCode": GROUPCODE,
                "date": DATE,
                "meridies": MERIDIES,
                "memberId": memberId,
                "temperature": temperature,
                "pin": pin}

    request = requests.post(url=SEND_URL, data=PAYLOAD)
    return request.text

def getMeridies(time):
    return MERIDIES_AM if int(time.split(":")[0]) < 12 else MERIDIES_PM

def getDateTime():
    now = datetime.now(timezone(TIME_ZONE))
    return now.strftime("%d/%m/%Y %H:%M:%S")

def getDateTimeObject(dateTimeString):
    return datetime.strptime(dateTimeString, "%d/%m/%Y %H:%M:%S")

def isQueryValid(queryTime):
    timeNow = getDateTimeObject(getDateTime())
    try:
        delta = timeNow - queryTime
        if delta.total_seconds() / 60 < 1:
            print(str(delta.total_seconds()))
            return True
        else:
            return False
    except:
        print("[main.py] isQueryValid(): ERROR occurred")
        return False

def getSendTempCriteria(doesURLexist, doesPINexist, doesMemberexist):
    criteriaText = {"URL": "✔\n\n" if doesURLexist else "⚠ URL not set\! /setsendurl to set url\n\n",
                "PIN": "✔\n\n" if doesPINexist else "⚠ PIN not set\! /setsendpin to set pin\n\n",
                "Name": "✔" if doesMemberexist else "⚠ Sender not set\! /setsender to set sender"}
    criteria = "🏁 Criteria before using /sendtemp\n\n"
    for x in criteriaText:
        criteria += (x + ": " + criteriaText[x])
    return criteria

print("-----> V1.1 Deployment success! <-----")