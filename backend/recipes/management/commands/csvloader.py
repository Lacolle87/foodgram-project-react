import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Импортировать ингредиенты и теги из CSV-файлов'

    def handle(self, *args, **options):
        csv_dir = settings.CSV_FILES_DIR
        csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]

        ingredients_to_create = self.parse_ingredients(csv_dir, csv_files)
        tags_to_create = self.parse_tags(csv_dir, csv_files)

        self.import_data(ingredients_to_create, tags_to_create)

    def parse_ingredients(self, csv_dir, csv_files):
        ingredients_to_create = []
        for csv_file_name in csv_files:
            csv_file_path = os.path.join(csv_dir, csv_file_name)
            with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    if 'name' in row and 'measurement_unit' in row:
                        name = row['name']
                        measurement_unit = row['measurement_unit']
                        ingredient = Ingredient(
                            name=name,
                            measurement_unit=measurement_unit)
                        ingredients_to_create.append(ingredient)
        return ingredients_to_create

    def parse_tags(self, csv_dir, csv_files):
        tags_to_create = []
        for csv_file_name in csv_files:
            csv_file_path = os.path.join(csv_dir, csv_file_name)
            with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    if 'name' in row and 'color' in row and 'slug' in row:
                        name = row['name']
                        color = row['color']
                        slug = row['slug']
                        tag = Tag(name=name, color=color, slug=slug)
                        tags_to_create.append(tag)
        return tags_to_create

    def import_data(self, ingredients_to_create, tags_to_create):
        try:
            if ingredients_to_create:
                Ingredient.objects.bulk_create(ingredients_to_create)
            if tags_to_create:
                Tag.objects.bulk_create(tags_to_create)
            self.stdout.write(
                self.style.SUCCESS(
                    'Ингредиенты и теги успешно импортированы.')
            )
        except Exception as err:
            log_file_path = os.path.join(settings.LOGS_DIR, 'import_data.log')
            with open(log_file_path, 'a') as log_file:
                log_file.write(f"Ошибка импорта данных: {str(err)}\n")
