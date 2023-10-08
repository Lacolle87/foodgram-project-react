import io
from django.utils import timezone

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def convert_pdf(data, title, font, font_size):
    """Конвертирует данные в pdf-файл при помощи ReportLab."""

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    # Устанавливаем заголовок PDF-файла
    p.setTitle(title)

    # Регистрация шрифта
    pdfmetrics.registerFont(TTFont(font, f'./fonts/{font}.ttf'))

    # Заголовок
    p.setFont(font, font_size)
    height = 800
    p.drawString(50, height, f'{title}:')
    height -= 30

    # Тело
    p.setFont(font, font_size)
    for i, (name, info) in enumerate(data.items(), 1):
        p.drawString(75, height, (f'{i}. {name} - {info["amount"]} '
                                  f'{info["measurement_unit"]}'))
        height -= 30

    # Подпись
    current_year = timezone.now().year
    signature = f'Спасибо, что используете Foodgram Project © {current_year}'
    p.line(50, height, 550, height)
    height -= 10
    p.setFont(font, font_size - 4)
    p.drawString(50, height, signature)
    p.showPage()
    p.save()
    buffer.seek(0)

    return buffer
