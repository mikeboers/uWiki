import re


def urlify_name(x):
    return re.sub(r'[^a-zA-Z0-9]', '-', x).strip('-')

