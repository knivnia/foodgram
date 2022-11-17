from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def http2pdf(response, list):
    pdfmetrics.registerFont(TTFont('Georgia', 'Georgia.ttf', 'UTF-8'))
    page = canvas.Canvas(response)
    page.setFont('Georgia', size=24)
    page.drawString(200, 800, 'Shopping list')
    page.setFont('Georgia', size=16)
    height = 750
    for i, (name, data) in enumerate(list.items(), 1):
        page.drawString(75, height, (f'{i}. {name} - {data["amount"]}, '
                                     f'{data["measurement_unit"]}'))
        height -= 25
    page.showPage()
    page.save()
