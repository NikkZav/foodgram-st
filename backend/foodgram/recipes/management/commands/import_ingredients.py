import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import ingredients from a JSON file into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to the JSON file containing ingredients data'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            self.stderr.write(f"Error: File {file_path} not found")
            return
        except json.JSONDecodeError:
            self.stderr.write(f"Error: File {file_path} is not a valid JSON")
            return

        created_count = 0
        for item in data:
            # Предполагаем, что JSON содержит поля модели Ingredient
            try:
                ingredient, created = Ingredient.objects.get_or_create(
                    name=item['fields']['name'],
                    measurement_unit=item['fields']['measurement_unit']
                )
                if created:
                    created_count += 1
            except KeyError as e:
                self.stderr.write(f"Error: Missing field {e} in JSON data")
                continue
            except Exception as e:
                self.stderr.write(f"Error processing item {item}: {e}")
                continue

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported {created_count} new ingredients"
            )
        )
