import numpy as np
import gzip
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

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

# Przekształcenie obrazów 28x28 do jednego wektora o długości 784 (28*28)
X_train = train_images.reshape(-1, 28 * 28)
X_test = test_images.reshape(-1, 28 * 28)

# Stworzenie klasyfikatora Random Forest
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)

# Trenowanie modelu
rf_model.fit(X_train, train_labels)

# Predykcja na zbiorze testowym
y_pred = rf_model.predict(X_test)

# Ocena dokładności modelu
accuracy = accuracy_score(test_labels, y_pred)
print(f"Dokładność modelu: {accuracy:.4f}")

# Raport klasyfikacji
print("Raport klasyfikacji:")
print(classification_report(test_labels, y_pred))

# Macierz błędów
plt.figure(figsize=(8, 6))
sns.heatmap(confusion_matrix(test_labels, y_pred), annot=True, fmt='d', cmap='Blues')
plt.title('Macierz błędów')
plt.xlabel('Przewidywane')
plt.ylabel('Rzeczywiste')
plt.show()
