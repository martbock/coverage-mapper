from enum import Enum


class NetworkType(str, Enum):
    NR = "NR",
    LTE = "LTE",
    GSM = "GSM",
