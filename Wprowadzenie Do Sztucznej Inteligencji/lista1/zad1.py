import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
import numpy as np
import gzip
import os

# Funkcja do wczytywania danych EMNIST MNIST
def load_emnist_images(file_path):
    with gzip.open(file_path, 'rb') as f:
        return np.frombuffer(f.read(), np.uint8, offset=16).reshape(-1, 28, 28)

def load_emnist_labels(file_path):
    with gzip.open(file_path, 'rb') as f:
        return np.frombuffer(f.read(), np.uint8, offset=8)

# Wczytanie danych
train_images = load_emnist_images('emnist-mnist-train-images-idx3-ubyte.gz')
train_labels = load_emnist_labels('emnist-mnist-train-labels-idx1-ubyte.gz')
test_images = load_emnist_images('emnist-mnist-test-images-idx3-ubyte.gz')
test_labels = load_emnist_labels('emnist-mnist-test-labels-idx1-ubyte.gz')

# Normalizacja danych
train_images = train_images / 255.0
test_images = test_images / 255.0

# Budowanie modelu sieci neuronowej
model = models.Sequential([
    layers.Flatten(input_shape=(28, 28)),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(10, activation='softmax')
])

# Kompilacja modelu
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Trenowanie modelu
model.fit(train_images, train_labels, epochs=10, batch_size=32, validation_split=0.1)

# Zapisanie modelu
model.save('trained_model.h5')

# Ewaluacja modelu
test_loss, test_accuracy = model.evaluate(test_images, test_labels)
print(f'Test Accuracy: {test_accuracy * 100:.2f}%')

# Obliczenie czułości i precyzji
from sklearn.metrics import classification_report
predictions = np.argmax(model.predict(test_images), axis=1)
report = classification_report(test_labels, predictions, digits=4)
print(report)
