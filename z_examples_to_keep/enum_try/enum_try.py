from enum import IntFlag, auto

class stop_code(IntFlag):
    RUNNING =       auto()           # not stopped
    NORMAL =        auto()
    MISFEED =       auto()
    DOUBLE_FEED =   auto()
    OTHER_ERROR =   auto()
    ERROR = MISFEED | DOUBLE_FEED | OTHER_ERROR


print('&', bool(stop_code.ERROR & stop_code.MISFEED))
print('&', bool(stop_code.ERROR & stop_code.RUNNING))
