import io
from datetime import datetime

from django.db.models import Sum
from django.db.models.query import QuerySet
from django.http import FileResponse
from recipes.models import Component
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def get_products(request) -> QuerySet:
    fields = ["ingredient__name", "amount", "ingredient__measurement_unit"]
    user = request.user
    products = (
        Component.objects.filter(recipe__shopping_cart__user=user)
        .values(fields[0])
        .annotate(  # продукты (ингредиенты) с одинаковым названием группируем
            amount=Sum("amount")  # и суммируем их количество (общее количество ингредиента)
        )
        .values_list(*fields)
        .order_by(fields[0])
    )
    return products


def download_shopping_cart_pdf(request) -> FileResponse:
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # регистрируем шрифты с поддержкой кириллицы
    pdfmetrics.registerFont(TTFont("DejaVu", "static/fonts/DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", "static/fonts/DejaVuSans-Bold.ttf"))

    products = get_products(request)

    # начальная вертикальная позиция (с отступом сверху)
    y = height - 40 * mm
    x = 20 * mm
    line_height = 10 * mm
    bottom_margin = 20 * mm

    # 1) Заголовок
    p.setFont("DejaVu-Bold", 16)
    title = f"Список покупок от {datetime.now():%d.%m.%Y (%H:%M)}"
    # рисуем фон заголовка: поднимаем y и рисуем прямоугольник высотой line_height*2
    header_height = line_height * 1
    p.setFillColor(colors.burlywood)
    p.rect(
        x,
        y - header_height + 5,
        width - 2 * x,
        header_height,
        fill=True,
        stroke=False,
    )
    # рисуем текст поверх
    p.setFillColor(colors.black)
    p.drawString(x + 2, y - line_height / 2, title)
    y -= header_height

    # 2) Кол-во позиций
    p.setFont("DejaVu", 12)
    count_text = f"Всего позиций: {len(products)}"
    p.drawString(x + 2, y - line_height / 2, count_text)
    y -= line_height * 1.5  # дополнительный отступ

    # 3) Список позиций: зебра-полосы
    for idx, (name, amount, unit) in enumerate(products, start=1):
        # если не хватает места — новая страница
        if y < bottom_margin:
            p.showPage()
            y = height - 40 * mm
        # фон строки
        bg = colors.whitesmoke if idx % 2 else colors.lightgrey
        p.setFillColor(bg)
        p.rect(
            x,
            y - line_height + 3,
            width - 2 * x,
            line_height,
            fill=True,
            stroke=False,
        )
        # текст поверх
        p.setFillColor(colors.black)
        p.setFont("DejaVu", 12)
        p.drawString(x + 4, y - line_height / 2, f"{idx}. {name} — {amount} {unit}")
        y -= line_height

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="shopping_cart.pdf")
