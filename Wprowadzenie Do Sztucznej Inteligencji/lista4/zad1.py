import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.datasets import fetch_openml

# ==========================
# Pooling - zmniejszanie wymiarowości obrazów
# ==========================

def apply_pooling_and_flatten(data_flat: np.ndarray, pool_type: str = 'avg', kernel_size: int = 2, stride: int = 2, original_dim: int = 28) -> np.ndarray:
    # Konwersja danych do typu float32 jeśli potrzeba
    if data_flat.dtype != np.float32:
        data_flat = data_flat.astype(np.float32)

    n_samples = data_flat.shape[0]

    # Przekształcenie wektorów (784 cechy) w obrazy 28x28
    X_reshaped_2d = data_flat.reshape(n_samples, 1, original_dim, original_dim)
    X_tensor_pytorch = torch.from_numpy(X_reshaped_2d)

    # Wybór typu pooling: 'max' lub 'avg'
    if pool_type == 'max':
        pool_layer = nn.MaxPool2d(kernel_size=kernel_size, stride=stride)
    elif pool_type == 'avg':
        pool_layer = nn.AvgPool2d(kernel_size=kernel_size, stride=stride)  # zmniejsza np. 28x28 do 14x14
    else:
        raise ValueError("Error: Chose type 'max' or 'avg'")

    # Wykonanie pooling
    X_pooled_tensor = pool_layer(X_tensor_pytorch)

    # Spłaszczenie z powrotem do wektorów (np. 14x14 = 196 cech)
    X_final_features = X_pooled_tensor.view(n_samples, -1).numpy()

    return X_final_features

# ==========================
# Wizualizacja wyników
# ==========================

# Normalizacja obrazu centroidu do zakresu [0, 1] dla poprawnej wizualizacji
def normalize_centroid_image(centroid_image):
    if centroid_image.max() != centroid_image.min():
        centroid_image = (centroid_image - centroid_image.min()) / (centroid_image.max() - centroid_image.min())
    else:
        centroid_image = np.zeros_like(centroid_image)
    return centroid_image

# Wyświetlanie centroidów jako obrazy
def visualize_clusters(centroids: np.ndarray, title):
    n_clusters = centroids.shape[0]
    n_features = centroids.shape[1]

    display_dim = int(np.sqrt(n_features))  # przy założeniu obrazu kwadratowego
    cols = min(n_clusters, 5)
    rows = int(np.ceil(n_clusters / cols))

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 2, rows * 2))
    axes = axes.flatten()

    for i in range(n_clusters):
        centroid_image = centroids[i].reshape(display_dim, display_dim)
        centroid_image = normalize_centroid_image(centroid_image)

        ax = axes[i]
        ax.imshow(centroid_image, cmap='gray', vmin=0, vmax=1)
        ax.set_title(f'Cluster {i}')
        ax.axis('off')

    # Usunięcie pustych wykresów, jeśli nie są potrzebne
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    fig.suptitle(title, fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

# Wyświetlanie macierzy przypisań (prawdziwa cyfra vs przypisany klaster)
def plot_cluster_assignment_matrix(y_true: np.ndarray, y_pred: np.ndarray, n_clusters: int, true_labels_range: range = range(10), title: str = "Digits in Clusters"):
    assignment_matrix = np.zeros((len(true_labels_range), n_clusters), dtype=int)

    # Liczenie ile razy każda cyfra trafiła do każdego klastra
    for i in range(len(y_true)):
        true_label = int(y_true[i])
        predicted_cluster = y_pred[i]
        if 0 <= predicted_cluster < n_clusters:
            assignment_matrix[true_label, predicted_cluster] += 1

    # Normalizacja do procentów
    row_sums = assignment_matrix.sum(axis=1, keepdims=True)
    normalized_matrix = assignment_matrix / (row_sums + 1e-7)

    plt.figure(figsize=(n_clusters * 0.6, len(true_labels_range) * 0.6))
    sns.heatmap(normalized_matrix, annot=True, fmt=".2f", cmap="Blues", cbar=True,
                linewidths=.5, linecolor="black", yticklabels=[str(label) for label in true_labels_range])
    plt.xlabel("Cluster")
    plt.ylabel("True digit")
    plt.title(title)
    plt.tight_layout()
    plt.show()

# ==========================
# Algorytm KMeans - krok po kroku
# ==========================
# Działanie algorytmu KMeans:
# 1. Inicjalizacja centroidów (losowo, inspirowana KMeans++).
# 2. Przypisanie punktów do najbliższych centroidów.
# 3. Aktualizacja centroidów jako średnich punktów w klastrze.
# 4. 🔹 (d) Sprawdzenie warunku stopu – jeśli centroidy przesuwają się minimalnie, zatrzymaj.
# 5. 🔹 (e) Obliczenie bezwładności (inertia) – suma odległości punktów od centroidów.
# 6. Powtarzanie całego procesu kilka razy – wybierz model z najlepszą (najmniejszą) bezwładnością.

class KMeans:
    def __init__(self, n_clusters=8, max_iter=30, tol=1e-4, random_state=None):
        self.n_clusters = n_clusters  # liczba klastrów
        self.max_iter = max_iter  # maksymalna liczba iteracji
        self.tol = tol  # tolerancja (próg ruchu centroidów)
        self.random_state = random_state
        self.centroids = None
        self.cluster_assignments = None
        self.inertia = None  # suma odległości punktów od centroidów

    # Obliczanie dystansu euklidesowego
    def _euclidean_distance(self, point, centroids):
        return np.sqrt(np.sum((point - centroids) ** 2, axis=1))

    # Inicjalizacja centroidów (podobnie jak w KMeans++)
    def _initialize_centroids(self, data):
        if self.random_state is not None:
            np.random.seed(self.random_state)

        n_samples, n_features = data.shape
        centroids = np.zeros((self.n_clusters, n_features))
        centroids[0] = data[np.random.choice(n_samples)]  # pierwszy centroid losowo

        for k in range(1, self.n_clusters):
            distances_matrix = np.sqrt(np.sum((data[:, np.newaxis, :] - centroids[:k]) ** 2, axis=2))
            min_distances = np.min(distances_matrix ** 2, axis=1)
            probabilities = min_distances / np.sum(min_distances) if np.sum(min_distances) != 0 else np.ones_like(min_distances) / len(min_distances)
            centroids[k] = data[np.random.choice(n_samples, p=probabilities)]

        return centroids

    # Przypisanie punktów do najbliższych centroidów
    def _assign_to_clusters(self, data):
        assignments = np.zeros(data.shape[0], dtype=int)
        for i, point in enumerate(data):
            distances = self._euclidean_distance(point, self.centroids)
            assignments[i] = np.argmin(distances)
        return assignments

    # Aktualizacja centroidów jako średnich punktów przypisanych do danego klastra
    def _update_centroids(self, data, cluster_assignments):
        new_centroids = np.zeros_like(self.centroids)
        for i in range(self.n_clusters):
            points = data[cluster_assignments == i]
            if len(points) > 0:
                new_centroids[i] = np.mean(points, axis=0)
            else:
                new_centroids[i] = self.centroids[i]  # centroid zostaje jeśli brak przypisanych punktów
        return new_centroids

    # 🔹 (e) Obliczanie bezwładności (suma kwadratów odległości punktów od centroidów)
    def _calculate_inertia(self, data, cluster_assignments):
        inertia = 0.0
        for i in range(self.n_clusters):
            points = data[cluster_assignments == i]
            inertia += np.sum((points - self.centroids[i]) ** 2)
        return inertia

    # Główna pętla algorytmu KMeans
    def fit(self, data):
        self.centroids = self._initialize_centroids(data)
        for _ in range(self.max_iter):
            old_centroids = self.centroids.copy()
            self.cluster_assignments = self._assign_to_clusters(data)
            self.centroids = self._update_centroids(data, self.cluster_assignments)

            # 🔹 (d) Sprawdzenie warunku stopu – jeśli centroidy przesuwają się mniej niż tol, przerwij pętlę
            movement = np.sum(np.linalg.norm(self.centroids - old_centroids, axis=1))
            if movement < self.tol:
                break

        # 🔹 (e) Obliczanie bezwładności po zakończeniu algorytmu
        self.inertia = self._calculate_inertia(data, self.cluster_assignments)
        return self

    # Przypisanie nowych danych do istniejących centroidów
    def predict(self, data):
        return self._assign_to_clusters(data)

# ==========================
# Wiele prób KMeans i wybór najlepszego modelu
# ==========================
def run_k_means_trials(data, labels, n_clusters, num_trials=5):
    best_model = None
    min_inertia = float('inf')

    for trial in range(num_trials):
        model = KMeans(n_clusters=n_clusters, max_iter=300, tol=1e-4, random_state=trial)
        model.fit(data)

        # 🔹 Wybór najlepszego modelu – wybieramy ten z najniższą bezwładnością
        if model.inertia < min_inertia:
            best_model = model
            min_inertia = model.inertia

    print(f"K={n_clusters} - Best inertia: {min_inertia:.2f}")
    
    # Wizualizacja wyników najlepszego modelu
    plot_cluster_assignment_matrix(y_true=labels, y_pred=best_model.cluster_assignments, n_clusters=n_clusters, title=f"Digit-cluster assignment (K={n_clusters})")
    visualize_clusters(best_model.centroids, f"Centroids (K={n_clusters})")
    return best_model

# ==========================
# Główna część programu
# ==========================
if __name__ == "__main__":
    # Pobranie zbioru MNIST
    images, labels = fetch_openml('mnist_784', version=1, return_X_y=True, as_frame=False)

    # Wykorzystanie 1000 pierwszych przykładów i normalizacja pikseli
    images = images[:1000] / 255.0
    labels = labels[:1000]

    # Redukcja wymiarowości za pomocą avg poolingu
    pooled_data = apply_pooling_and_flatten(images, pool_type='avg', kernel_size=2, stride=2)

    # Uruchomienie algorytmu KMeans dla różnych liczby klastrów
    for k in [10, 15, 20, 30]:
        run_k_means_trials(pooled_data, labels, n_clusters=k)
