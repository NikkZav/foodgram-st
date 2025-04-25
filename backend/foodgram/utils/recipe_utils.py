import string
import random
from recipes.models import ShortLink


def generate_unique_slug(length=6):
    characters = string.ascii_letters + string.digits
    while True:
        slug = ''.join(random.choices(characters, k=length))
        if not ShortLink.objects.filter(slug=slug).exists():
            return slug
