import re


def validate_fullname(fullname):
    # Check if fullname is a string and at least 4 characters long
    if not isinstance(fullname, str):
        return False
    if len(fullname) < 4:
        return False

    # Check if each part of the name is alphabetic
    for part in fullname.split():
        if not part.isalpha():
            return False

    return True


def validate_phone_number(phone_number):
    # Check if phone_number is a number, starts with 07, and has exactly 10 digits
    if not phone_number.isdigit():
        return False
    if len(phone_number) != 10:
        return False
    if not phone_number.startswith('07'):
        return False
    return True


def validate_id_number(id_number):
    # Check if id_number follows the pattern 00-000000A00
    pattern = re.compile(r'^\d{2}-\d{4,}[A-Za-z]\d{2}$')
    if not pattern.match(id_number):
        return False
    return True


def validate_dob(dob):
    # Check if dob is in the format YYYY-MM-DD
    try:
        year, month, day = map(int, dob.split('-'))
        if len(dob) != 10 or dob[4] != '-' or dob[7] != '-' or not (1900 <= year <= 9999) or not (
                1 <= month <= 12) or not (1 <= day <= 31):
            return False
    except ValueError:
        return False
    return True