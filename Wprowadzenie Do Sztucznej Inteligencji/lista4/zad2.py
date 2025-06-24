import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import time
import pandas as pd
from numba import njit
from sklearn.datasets import fetch_openml

# ==========================
# Pooling - redukcja wymiarowości obrazów
# ==========================
def apply_pooling_and_flatten(data_flat: np.ndarray, pool_type: str = 'max', kernel_size: int = 2, stride: int = 2, original_dim: int = 28) -> np.ndarray:
    # Konwersja danych do float32 jeśli potrzeba
    if data_flat.dtype != np.float32:
        data_flat = data_flat.astype(np.float32)
        
    n_samples = data_flat.shape[0]

    # Przekształcenie wektorów (784 cechy) w obrazy 28x28
    X_reshaped_2d = data_flat.reshape(n_samples, 1, original_dim, original_dim)
    X_tensor_pytorch = torch.from_numpy(X_reshaped_2d)

    # Wybór typu pooling
    if pool_type == 'max':
        pool_layer = nn.MaxPool2d(kernel_size=kernel_size, stride=stride)
    elif pool_type == 'avg':
        pool_layer = nn.AvgPool2d(kernel_size=kernel_size, stride=stride)
    else:
        raise ValueError("pool_type musi być 'max' lub 'avg'")

    # Wykonanie pooling
    X_pooled_tensor = pool_layer(X_tensor_pytorch)

    # Spłaszczenie wyników do wektorów
    X_final_features = X_pooled_tensor.view(n_samples, -1).numpy()
    
    return X_final_features

# ==========================
# Wizualizacja centroidów
# ==========================
def normalize_centroid_image(centroid_image):
    if centroid_image.max() != centroid_image.min():
        centroid_image = (centroid_image - centroid_image.min()) / (centroid_image.max() - centroid_image.min())
    else:
        centroid_image = np.zeros_like(centroid_image)
    return centroid_image

def visualize_clusters(centroids: np.ndarray, title):
    n_clusters = centroids.shape[0]
    n_features = centroids.shape[1]
    display_dim = int(np.sqrt(n_features))

    cols = min(n_clusters, 5)
    rows = int(np.ceil(n_clusters / cols))

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 3, rows * 3))
    if rows == 1 and cols == 1:
        axes = np.array([axes]) 
    else:
        axes = axes.flatten() 

    for i in range(n_clusters):
        centroid_image = centroids[i].reshape(display_dim, display_dim)
        centroid_image = normalize_centroid_image(centroid_image)

        ax = axes[i]
        ax.imshow(centroid_image, cmap='gray', vmin=0, vmax=1)
        ax.set_title(f'Klaster {i}')
        ax.axis('off')

    # Usunięcie pustych wykresów
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    fig.suptitle(title, fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) 
    plt.show()

# ==========================
# Wyliczanie pseudo-centroidów dla DBSCAN
# ==========================
def get_cluster_pseudo_centroids(data: np.ndarray, labels: np.ndarray, noise_label: int = -1) -> list[np.ndarray]:
    pseudo_centroids = []
    unique_cluster_labels = np.unique(labels)

    sorted_labels = sorted(unique_cluster_labels)

    for cluster_id in sorted_labels:
        if cluster_id == noise_label:
            continue  # Pomijamy punkty uznane za szum

        points_in_cluster = data[labels == cluster_id]

        if len(points_in_cluster) > 0:
            pseudo_centroid = np.mean(points_in_cluster, axis=0)
            pseudo_centroids.append(pseudo_centroid)

    return pseudo_centroids

# ==========================
# Wykres k-odległości dla doboru eps
# ==========================
from sklearn.neighbors import NearestNeighbors 

def plot_k_distance_graph(data: np.ndarray, min_samples: int = 5):
    # Obliczanie odległości do min_samples-tego najbliższego sąsiada
    neigh = NearestNeighbors(n_neighbors=min_samples + 1)
    neigh.fit(data)

    distances, indices = neigh.kneighbors(data)

    k_distances = np.sort(distances[:, min_samples], axis=0)

    plt.figure(figsize=(10, 6))
    plt.plot(k_distances)
    plt.xlabel("Punkty danych posortowane według odległości")
    plt.ylabel(f"Odległość do {min_samples}-tego najbliższego sąsiada")
    plt.title(f"Wykres k-Odległości dla min_samples = {min_samples}")
    plt.grid(True)
    plt.show()

# ==========================
# Algorytm DBSCAN - krok po kroku
# ==========================
class DBSCAN:
    # Kody specjalne: punkt nieprzypisany (0) i punkt szumowy (-1)
    UNCLASSIFIED = 0
    NOISE = -1

    def __init__(self, eps: float, min_samples: int):
        if eps <= 0:
            raise ValueError("Parametr 'eps' musi być większy od 0.")
        if min_samples < 1:
            raise ValueError("Parametr 'min_samples' musi być większy lub równy 1.")

        self.eps = eps
        self.min_samples = min_samples
        self.labels_ = None

    # ==========================
    # DBSCAN - szczegółowe kroki:
    # 1. Ustaw eps i min_samples.
    # eps (epsilon) – maksymalna odległość między dwoma punktami, aby były sąsiadami.
    # min_samples – minimalna liczba punktów, jaka musi być w sąsiedztwie punktu, żeby rozpocząć tworzenie klastra.
    # 2. Oznacz wszystkie punkty jako UNCLASSIFIED.
    # 3. Iteruj po wszystkich punktach:
    #    a) Jeśli punkt już przypisany → pomiń.
    #    b) Znajdź sąsiadów w promieniu eps.
    # 4. Jeśli punkt ma mniej sąsiadów niż min_samples → oznacz jako NOISE.
    # 5. Jeśli punkt ma wystarczająco sąsiadów → rozpocznij nowy klaster.
    # 6. Rozszerz klaster:
    #    - Przypisz sąsiadów do klastra.
    #    - Dodaj nieprzypisanych sąsiadów do kolejki do sprawdzenia.
    # 7. Powtarzaj aż wszystkie punkty zostaną odwiedzone.
    # 8. Zwróć etykiety klastrów.
    # ==========================

    def _euclidean_distance(self, point1: np.ndarray, point2: np.ndarray) -> float:
        return np.sqrt(np.sum((point1 - point2)**2))

    def _find_neighbors(self, data: np.ndarray, point_idx: int) -> list:
        distances = np.linalg.norm(data - data[point_idx], axis=1)
        neighbors = np.where(distances <= self.eps)[0].tolist()
        return neighbors

    def _expand_cluster(self, data: np.ndarray, labels: np.ndarray, point_idx: int, cluster_id: int):
        seed_set = [point_idx]
        labels[point_idx] = cluster_id

        i = 0
        while i < len(seed_set):
            current_point_idx = seed_set[i]
            neighbors = self._find_neighbors(data, current_point_idx)

            if len(neighbors) >= self.min_samples:
                for neighbor_idx in neighbors:
                    if labels[neighbor_idx] == self.NOISE or labels[neighbor_idx] == self.UNCLASSIFIED:
                        if labels[neighbor_idx] == self.UNCLASSIFIED:
                            seed_set.append(neighbor_idx)
                        labels[neighbor_idx] = cluster_id
            i += 1

    def fit_predict(self, X: np.ndarray) -> np.ndarray:
        n_samples = X.shape[0]
        self.labels_ = np.full(n_samples, self.UNCLASSIFIED, dtype=np.int32)

        current_cluster_id = 0

        for i in range(n_samples):
            if self.labels_[i] != self.UNCLASSIFIED:
                continue

            neighbors = self._find_neighbors(X, i)

            if len(neighbors) < self.min_samples:
                self.labels_[i] = self.NOISE
            else:
                current_cluster_id += 1
                self._expand_cluster(X, self.labels_, i, current_cluster_id)

        final_labels = np.full(n_samples, self.NOISE, dtype=np.int32)
        for i in range(n_samples):
            if self.labels_[i] > 0:
                final_labels[i] = self.labels_[i] - 1

        self.labels_ = final_labels
        return self.labels_

    def fit(self, X: np.ndarray):
        self.fit_predict(X)
        return self

# ==========================
# Główna część programu
# ==========================

# Pobranie danych MNIST
images, labels = fetch_openml('mnist_784', version=1, return_X_y=True, as_frame=False)
images_normalized = images / 255.0

# Użycie 1000 pierwszych przykładów
images_to_use = 1000
images_subset = images_normalized[:images_to_use]
labels_subset = labels[:images_to_use]

# Pooling (redukcja wymiarowości)
pooled_data = apply_pooling_and_flatten(images_subset, pool_type='avg', kernel_size=2, stride=2)

# Wykres k-odległości - pomaga dobrać eps
dbscan_min_samples_candidate = 100
plot_k_distance_graph(pooled_data, min_samples=dbscan_min_samples_candidate)

# Zestaw parametrów do testowania DBSCAN
avg_pooling_test_parameters = [
    (9, 1.1), (9, 1.15), (9, 1.22), (9, 1.4), (9, 1.45), (9, 1.5),
    (14, 1.2), (14, 1.28), (14, 1.32), (14, 1.65), (14, 1.7), (14, 1.74),
    (22, 1.28), (22, 1.33), (22, 1.39), (22, 1.85), (22, 1.92), (22, 1.98),
    (28, 1.3), (28, 1.38), (28, 1.43), (28, 2.1), (28, 2.18), (28, 2.26),
    (48, 1.35), (48, 1.43), (48, 1.48), (48, 2.2), (48, 2.35), (48, 2.45),
    (70, 1.42), (70, 1.48), (70, 1.53), (70, 2.3), (70, 2.48), (70, 2.58),
    (98, 1.48), (98, 1.52), (98, 1.58), (98, 2.55), (98, 2.65), (98, 2.75)
]

results_data = []

# Uruchamianie DBSCAN dla każdej kombinacji parametrów
for min_samples, eps in avg_pooling_test_parameters:
    print(f"\n--- Running DBSCAN for min_samples={min_samples}, eps={eps:.2f} ---")

    start_time = time.time()
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    dbscan_labels = dbscan.fit_predict(pooled_data)
    end_time = time.time()
    duration = end_time - start_time

    n_noise = np.sum(dbscan_labels == -1)
    total_points = len(dbscan_labels)
    noise_percentage = (n_noise / total_points) * 100

    unique_clusters = np.unique(dbscan_labels[dbscan_labels != -1])
    n_clusters = len(unique_clusters)

    results_data.append({
        "min_samples": min_samples,
        "eps": eps,
        "n_clusters": n_clusters,
        "%_noise": noise_percentage,
        "Time (s)": duration
    })

# Podsumowanie wyników
df_results = pd.DataFrame(results_data)
df_results['eps'] = df_results['eps'].round(2)
df_results['%_noise'] = df_results['%_noise'].round(2)
df_results['Time (s)'] = df_results['Time (s)'].round(2)

print(df_results.to_markdown(index=False))

# Finalne uruchomienie DBSCAN z wybranymi parametrami
eps = 1.9
min_samples = 8
dbscan = DBSCAN(eps=eps, min_samples=min_samples)
dbscan_labels = dbscan.fit_predict(pooled_data)

# Wyliczenie pseudo-centroidów i wizualizacja klastrów
dbscan_pseudo_centroids = get_cluster_pseudo_centroids(data=pooled_data, labels=dbscan_labels, noise_label=DBSCAN.NOISE)

visualize_clusters(np.array(dbscan_pseudo_centroids), title="Cluster Centroids (After Average Pooling)")
