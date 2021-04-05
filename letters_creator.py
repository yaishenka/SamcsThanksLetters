import os
import PyPDF2
from io import StringIO, BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
import settings
from google_sheets_reader import GoogleSheetsReader
from enum import Enum

pdfmetrics.registerFont(TTFont(settings.font_reg_name, settings.font_reg_file))
pdfmetrics.registerFont(TTFont(settings.font_for_name_name, settings.font_for_name_file))


class PdfString:
    def __init__(self, text, begin_point, font_name, font_size):
        self.begin_point = begin_point
        self.text = text
        self.font_name = font_name
        self.font_size = font_size


class Text:
    def __init__(self, font_size, line_spacing, list_size):
        self.strings = []
        self.font_size = font_size
        self.line_spacing = line_spacing
        self.list_size = list_size

    def add_string(self, text, font_name, font_size=None):
        if font_size is None:
            font_size = self.font_size
        print(self.list_size)
        print(stringWidth(text, font_name, font_size))
        x = (self.list_size - stringWidth(text, font_name, font_size)) / 2 + 121
        if not self.strings:
            begin_point = (x, settings.y_coordinate)
        else:
            begin_point = (x, self.strings[-1].begin_point[1] - self.line_spacing)
        pdf_string = PdfString(text, begin_point, font_name, font_size)
        self.strings.append(pdf_string)


class Participant:
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    default_list_size = can._pagesize[0]

    class DiplomType(Enum):
        POBED = 1
        PRIZER = 2
        UNDEFINED = 3

    def __init__(self, full_name, grade, diplom_type, school, town, list_size=default_list_size):
        self.full_name = full_name
        self.grade = str(grade)
        self.diplom_type = self.validate_diplom_type(diplom_type)
        self.school = school
        self.town = town
        self.list_size = list_size

        self.create_text()

    @staticmethod
    def validate_diplom_type(diplom_type):
        if diplom_type == 'Победитель':
            return Participant.DiplomType.POBED

        if diplom_type == 'Призёр':
            return Participant.DiplomType.PRIZER

        return Participant.DiplomType.UNDEFINED

    def create_text(self):
        text = Text(18, 50, self.list_size)
        first_str = self.full_name
        second_str = 'г. ' + self.town + ', ' + self.school + ', ' + self.grade + ' класс'

        text.add_string(first_str, font_name=settings.font_for_name_name, font_size=36)
        text.add_string(second_str, font_name=settings.font_reg_name, font_size=21)
        self.text = text

    def template_file(self):
        if self.diplom_type == self.DiplomType.PRIZER:
            return settings.priz_blank
        elif self.diplom_type == self.DiplomType.POBED:
            return settings.pob_blank
        else:
            raise ValueError('А что тут делает этот молодой человек?')

    def new_file(self, number):
        return os.path.join(settings.output_directory, number.__str__() + ') ' + self.full_name + '.pdf')


class LettersCreator:
    @staticmethod
    def create_letter(human, number):
        text = human.text
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        for string in text.strings:
            can.setFont(string.font_name, string.font_size)
            can.drawString(string.begin_point[0], string.begin_point[1], string.text)
        can.save()
        packet.seek(0)
        new_pdf = PyPDF2.PdfFileReader(packet)
        existing_pdf = PyPDF2.PdfFileReader(open(human.template_file(), "rb"))
        output = PyPDF2.PdfFileWriter()
        page = existing_pdf.getPage(0)
        page.mergePage(new_pdf.getPage(0))
        output.addPage(page)
        output_stream = open(human.new_file(number), "wb")
        output.write(output_stream)
        output_stream.close()

    @staticmethod
    def create_letters_from_table(table, sheet=0):
        all_records = GoogleSheetsReader.get_all_records(table, sheet)
        humans = []
        for record in all_records:
            human = Participant(record['fullname'], record['grade'], record['diplom_type'], record['school'],
                                record['city'])
            humans.append(human)

        letter_number = 1
        for human in humans:
            LettersCreator.create_letter(human, letter_number)
            letter_number += 1
