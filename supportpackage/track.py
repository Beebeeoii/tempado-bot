from datetime import datetime
from pytz import timezone
import requests
import json
import telegram
import os

TRACK_URL = os.environ["TRACK_URL"]
TIME_ZONE = os.environ["TIME_ZONE"]
MERIDIES_AM = "AM"
MERIDIES_PM = "PM"

def getDateTime():
    now = datetime.now(timezone(TIME_ZONE))
    return now.strftime("%d/%m/%Y %H:%M:%S")

def getMeridiesFromTime(time):
    return MERIDIES_AM if int(time.split(":")[0]) < 12 else MERIDIES_PM

def getGroupData(groupURL):
    try:
        OVERVIEW_CODE = groupURL[groupURL.rindex("/") + 1:]

        PAYLOAD = {"overviewCode": OVERVIEW_CODE,
            "date": getDateTime().split(" ")[0],
            "timezone": TIME_ZONE}
        
        response = requests.post(url=TRACK_URL, data=PAYLOAD, timeout=10)

        if response.status_code == requests.codes.ok:
            data = json.loads(response.text)

            return data
        else:
            response.raise_for_status()
    except:
        print("[track.py] getGroupTempData(): ERROR occured")

def getGroupNameData(data):
    return data["groupName"]

def getOverviewCodeData(data):
    return data["overviewURLCode"]

def getMemberTempData(data):
    return data["members"]

def formatReminder(data):    
    def emojiWrap(emoji, text):
        return emoji + " " + text + " " + emoji

    MEMBER_TEMP_DATA = getMemberTempData(data)
    MERIDIES = getMeridiesFromTime(getDateTime().split(" ")[1])

    message = []
    HEADING = "🏮 " + getGroupNameData(data) + " 🏮\n"

    message.append(HEADING)

    missingRecords = getMissingMembers(MEMBER_TEMP_DATA, MERIDIES)
    missingAM = missingRecords["amMissing"]
    missingPM = missingRecords["pmMissing"]

    if MERIDIES == MERIDIES_PM:
        if len(missingPM) == 0:
            message.append("🏆 All submitted PM temperature\! Well done\!\n")
        else:
            SUBTITLE = "__*Missing PM Temperature*__"
            message.append(SUBTITLE)
            message.extend(missingPM)
            message.append("")

    if len(missingAM) == 0:
        message.append("🏆 All submitted AM temperature\! Well done\!\n")
    else:
        SUBTITLE = "__*Missing AM Temperature*__"
        message.append(SUBTITLE)
        message.extend(missingAM)

    return "\n".join(message)

def getMissingMembers(memberTempData, meridies):
    def getRecords(memberData):
        records = {MERIDIES_AM: False, MERIDIES_PM: False}
        TEMP_RECORDS = memberData["tempRecords"]

        for record in TEMP_RECORDS:
            timeSent = record["recordForDateTime"]
            MERIDIES = getMeridiesFromTime(timeSent)
            if MERIDIES == MERIDIES_AM and not records[MERIDIES_AM]:
                records[MERIDIES_AM] = True
            elif MERIDIES == MERIDIES_PM and not records[MERIDIES_PM]:
                records[MERIDIES_PM] = True

            if records[MERIDIES_AM] and records[MERIDIES_PM]:
                return records
            
        return records
    
    amMissing = []
    pmMissing = []
    missingMembers = {"amMissing": amMissing, "pmMissing": pmMissing}

    for member in memberTempData:
        record = getRecords(member)

        if meridies == MERIDIES_PM:
            isPMSent = record[MERIDIES_PM]
            if not isPMSent:
                pmMissing.append(member["identifier"].upper())

        isAMSent = record[MERIDIES_AM]
        if not isAMSent:
            amMissing.append(member["identifier"].upper())

    return missingMembers