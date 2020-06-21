import requests
import os
import telegram
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from datetime import datetime
from pytz import timezone

FIREBASE_PROJECT_ID = os.environ["FIREBASE_PROJECT_ID"]
BOT_TOKEN = os.environ["TELEGRAM_TOKEN"]
SEND_URL = os.environ["SEND_URL"]
TRACK_URL = os.environ["TRACK_URL"]
TIME_ZONE = os.environ["TIME_ZONE"]
TIME_FORMAT = os.environ["TIME_FORMAT"]

cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': FIREBASE_PROJECT_ID,
})

db = firestore.client()

def statusCheck(a, b):
    sendOnline = isOnline(SEND_URL)
    trackOnline = isOnline(TRACK_URL)
    
    send_ref = db.collection("status").document("send")
    track_ref = db.collection("status").document("track")

    send_details_dict = send_ref.get().to_dict()
    track_details_dict = track_ref.get().to_dict()

    sendNoEntries = len(send_details_dict)
    trackNoEntries = len(track_details_dict)

    dateTimeNow = getDateTime()

    send_ref.set({
        dateTimeNow: sendOnline
    }, merge=True)

    track_ref.set({
        dateTimeNow: sendOnline
    }, merge=True)

    if sendNoEntries > 24:
        sortedDetails = list(send_details_dict)
        sortedDetails.sort()
        send_ref.update({
            sortedDetails[0]: firestore.DELETE_FIELD
        })
    
    if trackNoEntries > 24:
        sortedDetails = list(track_details_dict)
        sortedDetails.sort()
        track_ref.update({
            sortedDetails[0]: firestore.DELETE_FIELD
        })

def isOnline(url):
    try:
        sendStatus = requests.get(url, timeout=10)
        return True if sendStatus.status_code == 200 else False
    except:
        print(url, "cannot be reached.")
        return False

def getDateTime():
    return datetime.now(timezone(TIME_ZONE)).strftime(TIME_FORMAT)