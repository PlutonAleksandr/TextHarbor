import cv2
import joblib
import numpy as np


class SIFTClassifier:
    def __init__(self):
        # Используем SIFT для обнаружения ключевых точек и вычисления дескрипторов
        self.sift_params = dict(nfeatures=0, nOctaveLayers=3, contrastThreshold=0.04, edgeThreshold=10, sigma=1.6)
        self.sift = cv2.SIFT.create(**self.sift_params)
        self.bf = cv2.BFMatcher()

        self.train_data = []

    @staticmethod
    def normalize_descriptors(descriptors):
        # Нормализация дескрипторов
        if descriptors is not None:
            descriptors = descriptors / np.linalg.norm(descriptors, axis=1, keepdims=True)
        return descriptors

    def train(self, images, labels):
        for label, image in zip(labels, images):
            # Обнаруживаем ключевые точки и вычисляем дескрипторы с использованием SIFT
            keypoints, descriptors = self.sift.detectAndCompute(image, None)

            if descriptors is not None and len(descriptors) > 0:
                descriptors = self.normalize_descriptors(descriptors)
                self.train_data.append({"label": label, "descriptors": descriptors})

    def predict(self, test_image):
        if test_image is None:
            return None
            # Обнаруживаем ключевые точки и вычисляем дескрипторы тестового изображения с использованием SIFT
        keypoints, test_descriptors = self.sift.detectAndCompute(test_image, None)

        if test_descriptors is not None and len(test_descriptors) > 0:
            test_descriptors = self.normalize_descriptors(test_descriptors)

            best_match_label = None
            best_match_score = float('inf')

            for data in self.train_data:
                train_descriptors = data["descriptors"]

                # Используем метод ближайшего соседа для сопоставления дескрипторов
                matches = self.bf.match(test_descriptors, train_descriptors)

                # Вычисляем сумму расстояний (score) по всем совпадениям
                score = sum(match.distance for match in matches)

                if score < best_match_score:
                    best_match_score = score
                    best_match_label = data["label"]

            return best_match_label

    def save_model(self, filename):
        # Сохраняем параметры SIFT и другие необходимые данные
        model_data = {"sift_params": self.sift_params, "train_data": self.train_data}
        joblib.dump(model_data, filename)

    @classmethod
    def load_model(cls, filename):
        try:
            # Загружаем параметры SIFT и другие данные
            model_data = joblib.load(filename)

            # Создаем экземпляр классификатора с использованием параметров SIFT
            classifier = SIFTClassifier()
            classifier.sift = cv2.SIFT.create(**model_data["sift_params"])
            classifier.train_data = model_data["train_data"]

            return classifier
        except Exception as e:
            print(f"Error loading the model: {e}")
            return None
