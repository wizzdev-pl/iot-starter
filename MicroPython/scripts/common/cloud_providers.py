from typing import Tuple


class Providers:
    AWS = "AWS"
    KAA = "KAA"
    THINGSBOARD = "THINGSBOARD"
    BLYNK = "BLYNK"

    @classmethod
    def print_providers(cls) -> str:
        return "{}, {}, {}, {}".format(
            cls.AWS, cls.KAA, cls.THINGSBOARD, cls.BLYNK)

    @classmethod
    def get_providers(cls) -> Tuple[str, str, str]:
        return cls.AWS, cls.KAA, cls.THINGSBOARD, cls.BLYNK
