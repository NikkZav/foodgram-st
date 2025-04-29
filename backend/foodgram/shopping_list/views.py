import io
from datetime import datetime
from django.http import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from recipes.models import Component
from django.db.models import Sum
from django.db.models.query import QuerySet


def get_products(request) -> QuerySet:
    fields = ["ingredient__name", "amount", "ingredient__measurement_unit"]
    user = request.user
    products = Component.objects.filter(
        recipe__shopping_cart__user=user
    ).values(fields[0]).annotate(
        amount=Sum("amount")
    ).values_list(*fields).order_by(fields[0])
    print(products)
    print(type(products))
    return products


def download_shopping_cart_pdf(request) -> FileResponse:
    # Буфер в памяти
    buffer = io.BytesIO()

    # Настройка канвы
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Регистрируем шрифт, поддерживающий кириллицу
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'static/fonts/DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'static/fonts/DejaVuSans-Bold.ttf'))

    # Получаем продукты
    products = get_products(request)

    # Начальная позиция на странице
    x = 30
    y = height - 50
    line_height = 25

    # Устанавливаем шрифт
    p.setFont("DejaVuSans", 18)

    # Дата создания списка
    today = datetime.now().strftime("%d.%m.%Y")
    time = datetime.now().strftime("%H:%M")
    p.drawString(x, y, f"Список покупок от {today} ({time})")
    y -= line_height
    p.drawString(x, y, f"Количество продуктов в списке: {len(products)}")
    y -= 2 * line_height  # Пропуск строки

    # Проходимся по всем продуктам и пишем их
    for i, (name, amount, unit) in enumerate(products):
        line = f"{i + 1}.  {name} - {amount} {unit}"
        p.drawString(x, y, line)
        y -= line_height

        # Если строка не помещается, создаем новую страницу
        if y < 50:
            p.showPage()
            p.setFont("DejaVuSans", 14)
            y = height - 50
            p.drawString(x, y, f"Продолжение списка от {today}")
            y -= 2 * line_height

    # Завершить страницу
    p.showPage()
    p.save()

    # Вернуть как ответ
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="shopping_cart.pdf")
