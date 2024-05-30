
from django.forms import ValidationError


def validate_rating(value):
    if value < 0 or value > 5:
        raise ValidationError('Rating must be between 0 and 5.')


def validate_field_and_value(field, operator, value):
    allowed_fields = {
        'avg_rating': float,
        'title': str,
        'description': str,
        'ingredients': str,
        'preparation_steps': str,
        'cooking_time': int,
        'serving_size': int,
        'category_id': str
    }
    allowed_field_of_like_operator = ['title', 'description', 'ingredients',
                                      'preparation_steps', 'category_id']
    allowed_operators = ['=', '!=', 'in', 'not in', 'like']

    if field not in allowed_fields:
        raise ValidationError(f"Invalid field '{field}'. Fields must be one of: {', '.join(allowed_fields.keys())}.")

    if operator not in allowed_operators:
        raise ValidationError(f"Invalid Operator '{operator}'. Operator must be one of: {', '.join(allowed_operators)}.")
    
    # expected_type = allowed_fields[field]
    # if operator in ['in', 'not in'] and not all(isinstance(x, expected_type) for x in value):
    #     raise ValidationError(f"Invalid value type for field '{field}'. Expected {expected_type.__name__} of list.")

    # elif operator not in ['in', 'not in', 'like']:
        

    #     try:
    #         if expected_type == float:
    #             float(value)
    #         elif expected_type == int:
    #             int(value)
    #         elif expected_type == str:
    #             str(value)
    #         elif expected_type == list:
    #             list(value)
    #     except ValueError:
    #         raise ValidationError(f"Invalid value type for field '{field}'. Expected {expected_type.__name__}.")

    # elif operator == 'like':
    #     if field in allowed_field_of_like_operator:
    #         str(value)
    #     else:
    #         raise ValidationError(f"Only title, description, ingredients, preparation_steps, category_id these field are applicable for Like operator.")