# recipes/migrations/00XX_create_shortlink.py
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),  # или последняя применённая у тебя
    ]

    operations = [
        migrations.CreateModel(
            name='ShortLink',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('slug', models.SlugField(max_length=10, unique=True)),
                ('recipe', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='recipes.Recipe')),
            ],
        ),
    ]
