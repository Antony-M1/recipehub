# Generated by Django 5.0.6 on 2024-05-29 10:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_category_recipe_review'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='user_id',
            new_name='user',
        ),
    ]
