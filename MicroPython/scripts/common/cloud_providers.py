from typing import Tuple


class Providers:
    AWS = "AWS"
    KAA = "KAA"
    THINGSBOARD = "THINGSBOARD"
    BLYNK = "BLYNK"
    IBM = "IBM"

    @classmethod
    def print_providers(cls) -> str:
        return "{}, {}, {}, {}, {}".format(
            cls.AWS, cls.KAA, cls.THINGSBOARD, cls.BLYNK, cls.IBM)

    @classmethod
    def get_providers(cls) -> Tuple[str, ...]:
        return cls.AWS, cls.KAA, cls.THINGSBOARD, cls.BLYNK, cls.IBM
