import numpy as np
import gzip
import struct
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns

# Funkcja do wczytywania danych z formatu IDX (używanego w EMNIST)
def load_images(filename):
    with gzip.open(filename, 'rb') as f:
        # Wczytujemy dane
        f.read(4)  # Magic number
        num_images = struct.unpack('>I', f.read(4))[0]
        rows = struct.unpack('>I', f.read(4))[0]
        cols = struct.unpack('>I', f.read(4))[0]
        images = np.frombuffer(f.read(), dtype=np.uint8).reshape(num_images, rows * cols)
    return images

def load_labels(filename):
    with gzip.open(filename, 'rb') as f:
        # Wczytujemy etykiety
        f.read(4)  # Magic number
        num_labels = struct.unpack('>I', f.read(4))[0]
        labels = np.frombuffer(f.read(), dtype=np.uint8)
    return labels

# Ścieżki do danych EMNIST Digits
train_images_path = 'emnist-digits-train-images-idx3-ubyte.gz'
train_labels_path = 'emnist-digits-train-labels-idx1-ubyte.gz'
test_images_path = 'emnist-digits-test-images-idx3-ubyte.gz'
test_labels_path = 'emnist-digits-test-labels-idx1-ubyte.gz'

# Załaduj dane
X_train = load_images(train_images_path)
y_train = load_labels(train_labels_path)
X_test = load_images(test_images_path)
y_test = load_labels(test_labels_path)

# Podział na zbiór treningowy i testowy (jeśli dane są już podzielone, to ten krok można pominąć)
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=42)

# Tworzymy klasyfikator Random Forest
model = RandomForestClassifier(n_estimators=100, random_state=42)

# Trenujemy model
model.fit(X_train, y_train)

# Predykcja na zbiorze testowym
y_pred = model.predict(X_test)

# Ocena modelu
accuracy = accuracy_score(y_test, y_pred)
print(f"Dokładność modelu: {accuracy:.4f}")

# Raport z klasyfikacji
print("Raport klasyfikacji:")
print(classification_report(y_test, y_pred))

# Macierz błędów
plt.figure(figsize=(8, 6))
sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d', cmap='Blues')
plt.title('Macierz błędów')
plt.xlabel('Przewidywane')
plt.ylabel('Rzeczywiste')
plt.show()
