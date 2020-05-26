from datetime import datetime
from pytz import timezone
import os

class Time():
    def __init__(self):
        self.MERIDIES_AM = "AM"
        self.MERIDIES_PM = "PM"
        self.TIME_FORMAT = "%d/%m/%Y %H:%M:%S"
        self.TIME_ZONE = "Asia/Singapore"#os.environ["TIME_ZONE"]

    def getDateTime(self):
        now = datetime.now(timezone(self.TIME_ZONE))
        return now.strftime(self.TIME_FORMAT)
    
    def getDate(self):
        return self.getDateTime().split(" ")[0]

    def getTime(self):
        return self.getDateTime().split(" ")[1]

    def getMeridiesFromTime(self, time):
        return self.MERIDIES_AM if int(time.split(":")[0]) < 12 else self.MERIDIES_PM

    def getDateTimeObject(self, dateTimeString):
        return datetime.strptime(dateTimeString, self.TIME_FORMAT)