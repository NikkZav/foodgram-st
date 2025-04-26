import string
from django.db import models
from random import Random


CHARACTERS = string.ascii_letters + string.digits  # 62 символа
SALT = "foodgram"

urn_length = 3


def any_to_code(*args) -> list[int]:
    """Конвертирует переданные аргументы в список ASCII кодов.
    Встроенный hash() не используется, т.к. он не персистентный."""
    s = "".join(str(arg) for arg in args)  # Конкатенируем все аргументы в строку
    return [ord(x) for x in s]  # Конвертируем каждый символ в его ASCII код


def generate_urn(entity: models.Model, length=urn_length, seed=0) -> str:
    """Генерирует псевдо-уникальный urn определенной длины для переданной модели.
    Функция является персистентной, т.е. для одних и тех же входных данных
    всегда возвращает один и тот же результат."""
    entity_code = any_to_code(type(entity).__name__, entity.pk, SALT)
    Random(len(SALT) + entity.pk + seed).shuffle(
        entity_code
    )  # Перемешиваем для случайности
    entity_hash = "".join(str(c) for c in entity_code)  # Конвертируем в строку

    while len(entity_hash) < length:  # Увеличиваем длину хеша, если она меньше length
        entity_hash *= 2  # Просто дублируем хеш, чтобы увеличить его длину

    urn = ""
    for i in range(length):  # Разбиваем хеш на необходимое количество частей = length
        hash_part = "".join(
            entity_hash[i::length]
        )  # Берем числа из хэша с шагом length
        urn += CHARACTERS[int(hash_part) % len(CHARACTERS)]

    return urn


def generate_unique_urn(entity: models.Model, length=urn_length, seed=0) -> str:
    """Генерирует уникальный urn для переданной модели."""
    global urn_length
    if (
        length != urn_length
    ):  # Если длина urn изменилась, то обновляем глобальную переменную
        urn_length = length

    urn = generate_urn(entity, urn_length, seed)
    while entity.__class__.objects.filter(
        urn=urn
    ).exists():  # Проверяем, что urn уникален
        urn = generate_urn(
            entity, urn_length, seed + 1
        )  # Если не уникален, то новый urn
        seed += 1
        if seed > 10:  # Если не удалось сгенерировать уникальный urn за 10 попыток
            urn_length += 1  # То увеличиваем длину urn
            seed = 0
            if urn_length > 10:  # Если длина urn больше 10 символов, то...
                raise ValueError(
                    "Не удалось сгенерировать уникальный urn"
                )  # Выбрасываем ошибку
    return urn
