# Generated by Django 5.0.6 on 2024-05-30 05:30

import recipes.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_rename_user_id_recipe_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.IntegerField(validators=[recipes.validators.validate_rating]),
        ),
    ]
