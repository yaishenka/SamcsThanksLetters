account_credentials_file = 'acc2.json'  # Нужен для работы с API google таблиц

font_file = 'fonts/IBMPlexSans-Light.ttf'  # Файл шрифта (обязан быть в ttf)
font_name = 'IBMPlexSans-Light'  # Название шрифта

y_coordinate = 502  # y координата начала текста. Подбирается методом тыка :)

# Тут задается три шаблона. С текущим шаблоном прокатывает один и тот же,
# но по идее они могут быть разные для разного количества строк текста
normal_template_pdf = 'letter_templates/letter_blank.pdf'
longer_template_pdf = 'letter_templates/letter_blank.pdf'
longest_template_pdf = 'letter_templates/letter_blank.pdf'

output_directory = 'done_letters'  # Директория, куда будут писаться готовые письма. Убедитесь что она существует
