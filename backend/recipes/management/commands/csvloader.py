import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импортировать ингредиенты из CSV-файла'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file', type=str, help='Имя CSV-файла для импорта')

    def handle(self, *args, **options):
        csv_file_name = options['csv_file']
        csv_file_path = os.path.join(settings.CSV_FILES_DIR, csv_file_name)
        ingredients_to_create = []

        with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                name = row['name']
                measurement_unit = row['measurement_unit']

                ingredient = Ingredient(
                    name=name, measurement_unit=measurement_unit)
                ingredients_to_create.append(ingredient)

        try:
            Ingredient.objects.bulk_create(ingredients_to_create)
            self.stdout.write(self.style.SUCCESS(
                'Ингредиенты успешно импортированы.'))
        except Exception as err:
            log_file_path = os.path.join(
                settings.LOGS_DIR, 'import_ingredients.log')
            with open(log_file_path, 'a') as log_file:
                log_file.write(f"Ошибка импорта ингредиентов: {str(err)}\n")
