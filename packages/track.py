from .time_helper import Time
import requests
import json
import telegram
import os

TRACK_URL = os.environ["TRACK_URL"]
Time = Time()

def getGroupData(url):
    OVERVIEW_CODE = url[url.rindex("/") + 1:]

    PAYLOAD = {"overviewCode": OVERVIEW_CODE,
        "date": Time.getDate(),
        "timezone": Time.TIME_ZONE}
    
    response = requests.post(url=TRACK_URL, data=PAYLOAD, timeout=10)

    if response.status_code == requests.codes.ok:
        return json.loads(response.text)
    else:
        response.raise_for_status()

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
    MERIDIES = Time.getMeridiesFromTime(Time.getTime())

    message = []
    HEADING = "🏮 " + getGroupNameData(data) + " 🏮\n"

    message.append(HEADING)

    missingRecords = getMissingMembers(MEMBER_TEMP_DATA, MERIDIES)
    missingAM = missingRecords["amMissing"]
    missingPM = missingRecords["pmMissing"]

    if MERIDIES == Time.MERIDIES_PM:
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
        records = {Time.MERIDIES_AM: False, Time.MERIDIES_PM: False}
        TEMP_RECORDS = memberData["tempRecords"]

        for record in TEMP_RECORDS:
            timeSent = record["recordForDateTime"]
            MERIDIES = Time.getMeridiesFromTime(timeSent)
            if MERIDIES == Time.MERIDIES_AM and not records[Time.MERIDIES_AM]:
                records[Time.MERIDIES_AM] = True
            elif MERIDIES == Time.MERIDIES_PM and not records[Time.MERIDIES_PM]:
                records[Time.MERIDIES_PM] = True

            if records[Time.MERIDIES_AM] and records[Time.MERIDIES_PM]:
                return records
            
        return records
    
    amMissing = []
    pmMissing = []
    missingMembers = {"amMissing": amMissing, "pmMissing": pmMissing}

    for member in memberTempData:
        record = getRecords(member)

        if meridies == Time.MERIDIES_PM:
            isPMSent = record[Time.MERIDIES_PM]
            if not isPMSent:
                pmMissing.append(member["identifier"].upper())

        isAMSent = record[Time.MERIDIES_AM]
        if not isAMSent:
            amMissing.append(member["identifier"].upper())

    return missingMembers