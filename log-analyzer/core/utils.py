import re


def reg_date(value):
    return str(re.search('\d{4}\d{2}\d{2}', value).group())
