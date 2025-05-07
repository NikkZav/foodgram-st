# backend/foodgram/scripts/check_ingredients.py
import os
import sys
import django
from django.core.management import call_command

# Добавляем /app/ в PYTHONPATH
sys.path.append('/app')

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
django.setup()

from recipes.models import Ingredient


if Ingredient.objects.count() == 0:
    call_command('loaddata', '/app/data/db_ingredients.json')
    print("Ингредиенты успешно загружены.")
else:
    print("Ингредиенты уже загружены.")