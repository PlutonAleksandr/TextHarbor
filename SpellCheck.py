from language_tool_python import LanguageTool
import re
from concurrent.futures import ThreadPoolExecutor


class SpellCheck:
    def __init__(self, language: str):
        self.language_options = ["Русский", "Английский"]
        self.selected_language = language if language in self.language_options else None
        self.start_of_sentence = True

    def check_spelling_and_grammar(self, line: str):
        lang = 'ru-RU' if self.selected_language == self.language_options[0] else 'en-US'
        tool = LanguageTool(lang)
        matches = tool.check(line)
        return matches

    def correct_errors_in_line(self, line: str):
        matches = self.check_spelling_and_grammar(line)

        # Перебираем ошибки в обратном порядке, чтобы избежать проблем с изменением позиций
        for match in reversed(matches):
            if match.replacements:
                # Заменяем фрагмент с ошибкой на первую предложенную замену
                line = (
                    line[:match.offset] +
                    match.replacements[0] +
                    line[match.offset + match.errorLength:]
                )

        return line

    def correct_registers(self, line: str):
        new_line = []

        for word in re.findall(r'\b\w+\b|[.,!?;:]', line):
            if word.isalpha():
                # Исправляем регистры, если это не начало строки
                if not self.start_of_sentence:
                    word = word.lower()
                else:
                    # После слова включаем флаг начала строки
                    self.start_of_sentence = False
                    # Первую букву оставляем в верхнем регистре
                    word = word.capitalize()

            # После знаков включаем флаг начала строки
            elif word in ['.', '?', '!']:
                self.start_of_sentence = True

            new_line.append(word)

        new_line = ' '.join(new_line).strip()

        # Убираем лишние пробелы перед знаками препинания
        new_line = re.sub(r'\s+([.,!?;:])', r'\1', new_line)

        return new_line

    def correct_text(self, text: str):
        # Результат исправления
        result = []

        # исправление орфографии с использованием многопоточности
        with ThreadPoolExecutor() as executor:
            corrected_lines = list(executor.map(self.correct_errors_in_line, text.split('\n')))

        # исправление регистров
        for corrected_line in corrected_lines:
            corrected_string = self.correct_registers(line=corrected_line)
            result.append(corrected_string)
            result.append('\n')

        corrected_text = ''.join(result).strip()

        return corrected_text
