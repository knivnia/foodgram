# Generated by Django 4.1.2 on 2022-11-20 13:26

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0016_alter_recipe_cooking_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveIntegerField(help_text='Enter cooking time for your recipe', validators=[django.core.validators.MinValueValidator(1, message='Cooking time should be more than 0!')], verbose_name='Cooking time'),
        ),
    ]
