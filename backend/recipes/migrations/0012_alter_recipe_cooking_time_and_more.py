# Generated by Django 4.1.2 on 2022-11-20 12:58

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_alter_recipeingredients_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveIntegerField(help_text='Enter cooking time for your recipe', validators=[django.core.validators.MinValueValidator(1, message='Cooking time should be more than 0!')], verbose_name='Cooking time'),
        ),
        migrations.AlterField(
            model_name='recipeingredients',
            name='amount',
            field=models.PositiveSmallIntegerField(default=1, help_text='Add how much of ingredient you need for your recipe', validators=[django.core.validators.MinValueValidator(1, message='Amount of ingredient should be more than 0!')], verbose_name='Ingredient amount'),
        ),
    ]
