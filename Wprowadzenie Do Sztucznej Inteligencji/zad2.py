import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import to_categorical
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
from PIL import Image, ImageOps

# Funkcja do wczytywania własnych zdjęć
def load_custom_images(image_folder):
    images = []
    labels = []
    
    for file_name in os.listdir(image_folder):
        if file_name.endswith('.png') and file_name[0].isdigit():
            digit_label = int(file_name[0])
            image_path = os.path.join(image_folder, file_name)
            
            # Wczytaj obraz i popraw orientację
            img = Image.open(image_path).convert('L')
            img = img.rotate(-90, expand=True)  # Obrót o 90 stopni w prawo
            img = ImageOps.mirror(img)          # Odbicie lustrzane (opcjonalne)
            img = img.resize((28, 28))          # Zmiana rozmiaru na 28x28

            # Konwersja na tablicę NumPy + zamiana kolorów (negatyw)
            img_array = np.array(img) / 255.0
            img_array = 1.0 - img_array  # Zamiana kolorów
            img_array = np.expand_dims(img_array, axis=-1)
            
            images.append(img_array)
            labels.append(digit_label)

    return np.array(images), np.array(labels)

# Wczytanie modelu modelu
model = load_model("trained_model.h5")

# Wczytanie własnych obrazów
test_folder = "test_images"
custom_images, custom_labels = load_custom_images(test_folder)

# Klasyfikacja danych testowych
predictions = np.argmax(model.predict(custom_images), axis=1)

# Wyświetlanie wyników
print("Wyniki klasyfikacji:")
print(classification_report(custom_labels, predictions, digits=4))

# Wizualizacja wyników
def plot_images(images, labels, predictions):
    plt.figure(figsize=(10, 10))
    for i in range(min(25, len(images))):
        plt.subplot(5, 5, i + 1)
        plt.imshow(images[i].reshape(28, 28), cmap='gray')
        plt.title(f'Prawda: {labels[i]}\nPred: {predictions[i]}')
        plt.axis('off')
    plt.tight_layout()
    plt.show()

plot_images(custom_images, custom_labels, predictions)

# Macierz błędów (confusion matrix)
cm = confusion_matrix(custom_labels, predictions)
plt.figure(figsize=(8, 6))
plt.imshow(cm, cmap='Blues')
plt.title('Macierz błędów')
plt.colorbar()
plt.xlabel('Przewidywane')
plt.ylabel('Rzeczywiste')
plt.show()
