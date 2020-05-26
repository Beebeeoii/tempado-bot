def isSendPINValid(pin):
    try:
        int(pin)
    except:
        raise ValueError
    
    if len(pin) != 4:
        raise PINLengthError(pin)

    return True

class PINLengthError(Exception):
    def __init__(self, pin):
        super().__init__("Invalid PIN. Length != 4")