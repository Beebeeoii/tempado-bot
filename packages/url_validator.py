import requests
from .track import getGroupData

def isCheckURLValid(url):
    if not url.startswith("http"):
        raise MissingPrefixError(url)

    #may raise other errors eg. ConnectionError / Timeout
    if getGroupData(url) == None:
        raise InvalidURLError(url)
    else:
        return True

def isSendURLValid(url):
    if not url.startswith("http"):
        raise MissingPrefixError(url)

    TITLE = "Temperature Recording"
    HEADER = "RECORD YOUR TEMPERATURE"
    INVALID = "Invalid code"

    request = requests.post(url=url)
    response = request.text

    if INVALID in response:
        raise InvalidCodeError(url)
    elif TITLE not in response or HEADER not in response:
        raise InvalidURLError(url)
    else:
        return True

class MissingPrefixError(Exception):
    def __init__(self, url):
        super().__init__("Invalid URL. URL missing http prefix.")

class InvalidCodeError(Exception):
    def __init__(self, url):
        super().__init__("Invalid groupcode.")

class InvalidURLError(Exception):
    def __init__(self, url):
        super().__init__("Invalid URL. Is it even temptaking.ado.sg?")