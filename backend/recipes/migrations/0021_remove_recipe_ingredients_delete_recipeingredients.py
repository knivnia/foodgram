# Generated by Django 4.1.2 on 2022-11-04 23:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0020_alter_recipe_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='ingredients',
        ),
        migrations.DeleteModel(
            name='RecipeIngredients',
        ),
    ]
