import re


def sluggify_name(x):

    # Remove anything that looks like paths.
    x = re.sub(r'(^|/)\.+/', '/', x)

    # Strip spaces and slashes from ends.
    x = re.sub(r'^[\s/]+', '', x)
    x = re.sub(r'[\s/]+$', '', x)

    # Normalize type & qty of spaces.
    x = re.sub(r'\s+', ' ', x)

    # Strip whitespace around slashes.
    x = re.sub(r'\s*/\s*', '/', x)
    
    return x


def urlify_name(x):
    return re.sub(r'[^a-zA-Z0-9]', '-', x).strip('-')

