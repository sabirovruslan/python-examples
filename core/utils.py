import re


def reg_date(value):
    return re.match(r'^.*-(\d+)\.?\w*$', value)[0]