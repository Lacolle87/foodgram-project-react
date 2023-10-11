import io
from django.utils import timezone

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def convert_pdf(data, title, font, font_size):
    """Конвертирует данные в pdf-файл при помощи ReportLab."""

    buffer = io.BytesIO()
    pdf_canvas = canvas.Canvas(buffer, pagesize=A4)

    # Устанавливаем заголовок PDF-файла
    pdf_canvas.setTitle(title)

    # Регистрация шрифта
    pdfmetrics.registerFont(TTFont(font, f'./fonts/{font}.ttf'))

    # Заголовок
    pdf_canvas.setFont(font, font_size)
    height = 800
    pdf_canvas.drawString(50, height, f'{title}:')
    height -= 30

    # Тело
    pdf_canvas.setFont(font, font_size)
    for index, (name, info) in enumerate(data.items(), 1):
        pdf_canvas.drawString(75, height,
                              (f'{index}. {name} - {info["amount"]} '
                               f'{info["measurement_unit"]}'))
        height -= 30

    # Подпись
    current_year = timezone.now().year
    signature = f'Спасибо, что используете Foodgram Project © {current_year}'
    pdf_canvas.line(50, height, 550, height)
    height -= 10
    pdf_canvas.setFont(font, font_size - 4)
    pdf_canvas.drawString(50, height, signature)
    pdf_canvas.showPage()
    pdf_canvas.save()
    buffer.seek(0)

    return buffer
