import os
import django
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodgram.settings")

django.setup()

from recipes.models import Ingredient


def load_ingredients_from_csv(file_path):
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            name = row['name']
            measurement_unit = row['measurement_unit']

            ingredient = Ingredient.objects.create(
                name=name,
                measurement_unit=measurement_unit
            )
            ingredient.save()

load_ingredients_from_csv('data/ingredients.csv')
