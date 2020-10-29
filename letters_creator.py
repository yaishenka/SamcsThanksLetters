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

pdfmetrics.registerFont(TTFont(settings.font_name, settings.font_file))


class PdfString:
    def __init__(self, text, begin_point):
        self.begin_point = begin_point
        self.text = text


class Text:
    def __init__(self, font_size, line_spacing, list_size):
        self.strings = []
        self.font_size = font_size
        self.line_spacing = line_spacing
        self.list_size = list_size

    def add_string(self, text):
        x = (self.list_size - stringWidth(text, settings.font_name, self.font_size)) / 2
        if not self.strings:
            begin_point = (x, settings.y_coordinate)
        else:
            begin_point = (x, self.strings[-1].begin_point[1] - self.line_spacing)
        pdf_string = PdfString(text, begin_point)
        self.strings.append(pdf_string)


class HumanToCongratulate:
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    default_list_size = can._pagesize[0]

    def __init__(self, post, full_name, town, school, list_size=default_list_size):
        self.post = post
        self.full_name = full_name
        self.town = town
        self.school = school
        self.list_size = list_size
        self.type = ''

        self.normal_text = ''
        self.longer_text = ''
        self.longest_text = ''

        self.create_normal()
        self.create_longer()
        self.create_longest()

    def create_normal(self):
        text = Text(18, 24, self.list_size)
        first_str = self.post + ' ' + self.school + ' ' + self.town
        second_str = self.full_name

        if len(first_str) < 40:
            self.type = 'normal'
        text.add_string(first_str)
        text.add_string(second_str)
        self.normal_text = text

    def create_longer(self):
        text = Text(18, 24, self.list_size)
        first_str = self.post + ' ' + self.school
        second_str = self.town
        third_str = self.full_name

        if len(first_str) < 40 and not self.type:
            self.type = 'longer'

        text.add_string(first_str)
        text.add_string(second_str)
        text.add_string(third_str)
        self.longer_text = text

    def create_longest(self):
        text = Text(16, 20, self.list_size)
        first_str = self.post + ' ' + self.school
        second_str = self.town
        third_str = self.full_name

        if not self.type:
            self.type = 'longest'

        text.add_string(first_str)
        text.add_string(second_str)
        text.add_string(third_str)
        self.longest_text = text

    def right_text(self):
        if self.type == 'normal':
            return self.normal_text
        elif self.type == 'longer':
            return self.longer_text
        else:
            return self.longest_text

    def template_file(self):
        if self.type == 'normal':
            return settings.normal_template_pdf
        elif self.type == 'longer':
            return settings.longer_template_pdf
        else:
            return settings.longest_template_pdf

    def new_file(self, number):
        return os.path.join(settings.output_directory, number.__str__() + ') ' + self.full_name + '.pdf')


class LettersCreator:
    @staticmethod
    def create_letter(human, number):
        text = human.right_text()
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        can.setFont(settings.font_name, text.font_size)
        for string in text.strings:
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
            human = HumanToCongratulate(record['post'], record['fullname'], record['city'], record['school'])
            humans.append(human)

        letter_number = 1
        for human in humans:
            LettersCreator.create_letter(human, letter_number)
            letter_number += 1
