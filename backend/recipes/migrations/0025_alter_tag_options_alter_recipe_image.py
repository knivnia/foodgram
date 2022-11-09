# Generated by Django 4.1.2 on 2022-11-09 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0024_recipe_ingredients'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ['id']},
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(blank=True, help_text='Upload your image', upload_to='recipes/', verbose_name='Image'),
        ),
    ]
