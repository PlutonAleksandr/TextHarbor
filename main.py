from tkinter import *
from tkinter import messagebox, filedialog
from tkinter.ttk import Progressbar
import pyperclip
import cv2
import numpy as np

from SpellCheck import SpellCheck
from selection import AreaSelection
from letterExtraction import LetterExtraction as le
from SIFTClassifier import SIFTClassifier


class Interface:
    def __init__(self, window):
        self.window = window
        self.window.title("Image Editor")
        self.window.geometry("500x150")
        self.window.iconbitmap('icon.ico')
        self.window.resizable(False, False)

        self.area_label = Label(self.window, text="Изображение:")
        self.area_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.area_options = ["Часть экрана", "Файл"]
        self.area_var = StringVar(self.window)
        self.area_var.set(self.area_options[0])
        self.area_menu = OptionMenu(self.window, self.area_var, *self.area_options)
        self.area_menu.config(width=20)
        self.area_menu.grid(row=0, column=1, padx=10, pady=5)

        self.language_label = Label(self.window, text="Язык:")
        self.language_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)

        self.language_options = ["Русский", "Английский"]
        self.language_var = StringVar(self.window)
        self.language_var.set(self.language_options[0])
        self.language_menu = OptionMenu(self.window, self.language_var, *self.language_options)
        self.language_menu.config(width=20)
        self.language_menu.grid(row=1, column=1, padx=10, pady=5)

        self.transfer_label = Label(self.window, text="Передать:")
        self.transfer_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)

        self.transfer_options = ["Текст в буфер обмена", "Текст в файл"]
        self.transfer_var = StringVar(self.window)
        self.transfer_var.set(self.transfer_options[0])
        self.transfer_menu = OptionMenu(self.window, self.transfer_var, *self.transfer_options)
        self.transfer_menu.config(width=20)
        self.transfer_menu.grid(row=2, column=1, padx=10, pady=5)

        self.load_button = Button(self.window, text="Получить\nизображение", command=self.get_image, height=5)
        self.load_button.grid(row=0, column=2, rowspan=3, padx=10, pady=5)

        self.area = None

    def get_image(self):
        """
        получение изображения
        """
        area_choice = self.area_var.get()
        if area_choice == self.area_options[0]:
            AreaSelection(self.window, self.recognition)
        elif area_choice == self.area_options[1]:
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
            if file_path:
                image = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
                if image is not None:
                    self.recognition(image)
                else:
                    messagebox.showerror("Ошибка", "Не удалось загрузить изображение.")

    def get_language_model(self):
        """
        получение языковой модели
        """
        language_choice = self.language_var.get()
        return "SIFTClassifier_RU.joblib" if language_choice == self.language_options[0] else "SIFTClassifier_EN.joblib"

    def output_text(self, text: str):
        transfer_choice = self.transfer_var.get()  # Получаем выбор пользователя
        if transfer_choice == self.transfer_options[0]:
            pyperclip.copy(text)
            if text != "":
                messagebox.showinfo("Успех", "Текст успешно скопирован в буфер обмена!")
        elif transfer_choice == self.transfer_options[1]:
            # Запросить у пользователя имя файла для сохранения
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if file_path:
                # Открыть файл для записи и записать в него текст
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(text)
                messagebox.showinfo("Успех", f"Текст успешно сохранен в файле: {file_path}")

    def show_progress_bar(self):
        window_progresbar = Toplevel(self.window)
        window_progresbar.title("Progress")
        window_progresbar.geometry("300x50")

        progressbar = Progressbar(window_progresbar, orient="horizontal", mode="determinate", maximum=100)
        progressbar.pack(side="top", fill="x", padx=10, pady=10, anchor="center")
        window_progresbar.lift(self.window)

        return window_progresbar, progressbar

    def recognition(self, img_txt):
        if img_txt is None:
            return 0

        window_progresbar, progressbar = self.show_progress_bar()

        def continue_recognition():
            self.area = cv2.cvtColor(img_txt, cv2.COLOR_RGB2BGR)
            l_ext = le(self.area)
            lines = l_ext.extract_letters()
            if len(lines) == 0:
                window_progresbar.destroy()
                messagebox.showinfo("Ошибка", f"Текст не найден")
                return 0

            language_model = self.get_language_model()
            classifier = SIFTClassifier().load_model(language_model)

            count_lines = len(lines)
            text = ""
            count_predict = 0
            for line in lines:

                for i in range(len(line)):
                    # the distance between = расстояние между
                    db = 0
                    if i < len(line) - 1:
                        db = line[i+1][1] - line[i][1] - line[i][2]

                    # проверка что это первая буква или буква после точки!!!!!!!!!!!!!

                    prediction = classifier.predict(line[i][4])
                    if prediction is not None:
                        text += prediction
                    if db > (line[i][2] / 5):
                        text += " "

                text += '\n'

                count_predict += 1
                progress_value = int(count_predict / count_lines * 100)
                progressbar["value"] = progress_value
                window_progresbar.update_idletasks()

            window_progresbar.destroy()
            checker = SpellCheck(language=self.language_var.get())
            text = checker.correct_text(text=text)
            self.output_text(text)

        self.window.after(100, continue_recognition)


if __name__ == "__main__":
    window = Tk()
    app = Interface(window)
    window.mainloop()
