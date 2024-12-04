""" Генерация pdf документа """
from fpdf import FPDF


# FPDF не поддерживает асинхронный вызов
def create_pdf(filename, item_data, description, names):
    """ Функция для создания pdf документа """

    pdf_filename = filename
    pdf = FPDF()
    pdf.add_page()

    pdf.add_font('DejaVuSans', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)
    pdf.set_font("DejaVuSans", size=12)
    pdf.cell(200, 10, txt=f"Отчет для элемента с ID: {id}", ln=True)
    pdf.cell(200, 10, txt=f"Название: {item_data['ИСН']}", ln=True)
    pdf.cell(200, 10, txt=f"Проблема: {item_data['problem']}", ln=True)
    pdf.cell(200, 10, txt=f"Дата: {item_data['date']}", ln=True)
    pdf.cell(200, 10, txt=f"Дополнительное описание: {description}", ln=True)
    pdf.cell(200, 10, txt=f"Список деталей: {', '.join(names)}", ln=True)

    pdf.output(pdf_filename)
