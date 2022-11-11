import re

from rest_framework import serializers


def hex_code_validator(code):
    if not re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', code):
        raise serializers.ValidationError('Invalid HEX-code!')
