import string
from django.db import models
from random import Random


CHARACTERS = string.ascii_letters + string.digits  # 62 символа
SALT = 'foodgram'


def any_to_code(*args) -> list[int]:
    '''Конвертирует переданные аргументы в список ASCII кодов.
    Встроенный hash() не используется, т.к. он не персистентный.'''
    s = ''.join(str(arg) for arg in args)  # Конкатенируем все аргументы в строку
    return [ord(x) for x in s]  # Конвертируем каждый символ в его ASCII код


def generate_slug(entity: models.Model, length=3, seed=0) -> str:
    '''Генерирует псевдо-уникальный slug определенной длины для переданной модели.
    Функция является персистентной, т.е. для одних и тех же входных данных
    всегда возвращает один и тот же результат.'''
    entity_code = any_to_code(type(entity).__name__, entity.pk, SALT)
    Random(len(SALT) + entity.pk + seed).shuffle(entity_code)  # Перемешиваем для случайности
    entity_hash = ''.join(str(c) for c in entity_code)  # Конвертируем в строку

    while len(entity_hash) < length:  # Увеличиваем длину хеша, если она меньше length
        entity_hash *= 2  # Просто дублируем хеш, чтобы увеличить его длину

    slug = ''
    for i in range(length):  # Разбиваем хеш на необходимое количество частей = length
        hash_part = ''.join(entity_hash[i::length])  # Берем числа из хэша с шагом length
        slug += CHARACTERS[int(hash_part) % len(CHARACTERS)]

    return slug


def generate_unique_slug(entity: models.Model, length=3, seed=0) -> str:
    '''Генерирует уникальный slug для переданной модели.'''
    slug = generate_slug(entity, length, seed)
    while entity.__class__.objects.filter(slug=slug).exists():  # Проверяем, что slug уникален
        slug = generate_slug(entity, length, seed + 1)  # Если не уникален, то генерируем новый slug
        seed += 1
        if seed > 10:  # Если не удалось сгенерировать уникальный slug за 10 попыток
            length += 1  # То увеличиваем длину slug
            seed = 0
            if length > 10:  # Если длина slug больше 10 символов, то...
                raise ValueError('Не удалось сгенерировать уникальный slug')  # Выбрасываем ошибку
    return slug



# class Model:
#     def __init__(self, pk):
#         self.pk = pk

# it = []
# epoch = 10
# for seed in range(epoch):
#     set_slugs = set()
#     i = seed * 123
#     start = i
#     while True:
#         entity = Model(i)
#         try:
#             slug = generate_unique_slug(entity, set_slugs)
#         except ValueError:
#             print(f'Не удалось сгенерировать уникальный slug на {i - start} итерации')
#         # if slug in set_slugs:
#         #     for seeed in range(2):
#         #         slug = generate_slug(i, seed=seeed + 1)
#         #         if slug not in set_slugs:
#         #             break  # Если нашли уникальный слаг, то выходим из цикла
#         if slug in set_slugs:
#             print(f'Коллизия на {i - start} итерации')
#             print(f'Слаг: {slug}')
#             break  # Если нашли коллизию, то выходим из цикла
#         set_slugs.add(slug)
#         i += 1
#     it += [i - start]

# print(f'Среднее количество итераций: {sum(it) / len(it)}')
