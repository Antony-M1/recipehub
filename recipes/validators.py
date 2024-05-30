
from django.forms import ValidationError


def validate_rating(value):
    if value < 0 or value > 5:
        raise ValidationError('Rating must be between 0 and 5.')