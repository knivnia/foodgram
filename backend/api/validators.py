import re

from django.core.exceptions import ValidationError


def hex_code_validator(code):
    if not re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', code):
        raise ValidationError('Invalid HEX-code!')
