import cv2
import numpy as np


class LetterExtraction:
    def __init__(self, img):
        self.image_file = img
        self.out_size = 30

    @staticmethod
    def increase_scale(img, scale):
        array = np.asarray(img)
        vert = len(array)
        gor = len(array[0])
        return cv2.resize(img, (gor * scale, vert * scale), interpolation=cv2.INTER_LANCZOS4)

    @staticmethod
    def difference_position(letter_one, letter_two):
        return letter_one[0] + letter_one[3] + 10 - letter_two[0]

    def sort_letters(self, letters):
        letters.sort(key=lambda y: (y[0], y[1]), reverse=False)

        result = []

        i = 0
        while i < len(letters):
            line = []
            for j in range(i, len(letters)):
                line.append(letters[j])
                i = j + 1
                if j < len(letters) - 1 and self.difference_position(letters[j], letters[j + 1]) < 0:
                    break

            line.sort(key=lambda x: x[1], reverse=False)

            line = self.combining_parts_symbols(line)
            line = self.combining_parts_symbols(line)
            result.append(line)

        return result

    @staticmethod
    def combining_parts_symbols(line):
        list_zam = []

        for id in range(len(line) - 1):
            cur = line[id]
            next = line[id + 1]
            if next[0] < cur[0] and (cur[1] + cur[2]) > next[1] + next[2]:
                res = cv2.vconcat([cv2.resize(next[4], (30, next[3])), cv2.resize(cur[4], (30, cur[3]))])
                list_zam.append((cv2.resize(res, (30, 30)), id))

        k = 0
        for el in list_zam:
            id = el[1] - k
            img = line[id]
            updated_img = (img[0], img[1], img[2], img[3], el[0])  # Создаем новый кортеж с обновленным изображением
            line[id] = updated_img
            del line[id + 1]
            k += 1

        return line

    def extract_letters(self, first=True):
        img = self.image_file
        img = self.increase_scale(img, 2)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if first:
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 51, 2)
        else:
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 51, 2)

        img_erode = thresh.copy()

        contours, hierarchy = cv2.findContours(img_erode, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        output = img.copy()

        letters = []
        for idx, contour in enumerate(contours):
            (x, y, w, h) = cv2.boundingRect(contour)
            # print(f"(x, y, w, h) = ({x, y, w, h}) ")
            if hierarchy[0][idx][3] == 0:
                cv2.rectangle(output, (x, y), (x + w, y + h), (70, 0, 0), 1)
                letter_crop = gray[y:y + h, x:x + w]

                size_max = max(w, h)
                letter_square = 255 * np.ones(shape=[size_max, size_max], dtype=np.uint8)

                if w > h:
                    y_pos = size_max // 2 - h // 2
                    letter_square[y_pos:y_pos + h, 0:w] = letter_crop
                elif w < h:
                    x_pos = size_max // 2 - w // 2
                    letter_square[0:h, x_pos:x_pos + w] = letter_crop
                else:
                    letter_square = letter_crop

                letters.append(
                    (
                        y,
                        x,
                        w,
                        h,
                        cv2.resize(letter_square, (self.out_size, self.out_size), interpolation=cv2.INTER_AREA)
                    )
                )

        if len(letters) == 0 and first:
            return self.extract_letters(first=False)

        return self.sort_letters(letters)
