import os
import telegram
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials

FIREBASE_PROJECT_ID = os.environ["FIREBASE_PROJECT_ID"]
BOT_TOKEN = os.environ["TELEGRAM_TOKEN"]

cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': FIREBASE_PROJECT_ID,
})

db = firestore.client()

def dailyTempCheckAm(a, b):
    bot = telegram.Bot(token=BOT_TOKEN)

    subscriber_ref = db.collection("subscribers").document("reminderSubscribers")
    subscriber_details = subscriber_ref.get()
    subscriber_details_dict = subscriber_details.to_dict()

    subscriberList = getSubscribers(subscriber_details_dict)

    reminderMsg = "🕚 Time now: 1100\n\n" + \
                    "/sendtemp to submit your AM temperature if you haven't already done so!"

    if subscriberList == -1:
        print("[getSubscribers()]: ERROR OCCURRED!")
        return

    for subscriber in subscriberList:
        try:
            bot.sendMessage(chat_id=int(subscriber), text=reminderMsg)
        except:
            subscriber_ref.update({
                subscriber: firestore.DELETE_FIELD
            })
    
    print("Function executed successfully!")

def getSubscribers(subscriber_details_dict):
    try:
        subscriberList = []
        for subscriber in subscriber_details_dict:
            if subscriber_details_dict[subscriber]:
                subscriberList.append(subscriber)
        return subscriberList
    except:
        return -1