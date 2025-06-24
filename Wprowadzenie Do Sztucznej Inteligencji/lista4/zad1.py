# ==========================
# Implementacja algorytmu KMeans
# ==========================

# Algorytm KMeans - działanie krok po kroku:
# 1. Losowo wybierz centroidy (z preferencją do rozproszenia - metoda podobna do KMeans++).
# 2. Przypisz każdy punkt do najbliższego centroidu (przypisanie do klastra).
# 3. Oblicz nowe centroidy jako średnie punktów w każdym klastrze.
# 4. Sprawdź warunek stopu - jeśli centroidy prawie się nie przesuwają, zakończ.
# 5. Oblicz bezwładność (suma odległości punktów od centroidów) - ocena jakości modelu.
# 6. Powtarzaj algorytm kilka razy z różnymi początkami, wybierz najlepszy model (z najniższą bezwładnością).

class KMeans:
    def __init__(self, n_clusters=8, max_iter=30, tol=1e-4, random_state=None):
        self.n_clusters = n_clusters  # liczba klastrów
        self.max_iter = max_iter  # maksymalna liczba iteracji
        self.tol = tol  # tolerancja dla zatrzymania (próg ruchu centroidów)
        self.random_state = random_state
        self.centroids = None
        self.cluster_assignments = None
        self.inertia = None  # suma odległości punktów od centroidów

    # Obliczanie odległości euklidesowej punktu od wszystkich centroidów
    def _euclidean_distance(self, point, centroids):
        return np.sqrt(np.sum((point - centroids) ** 2, axis=1))

    # Inicjalizacja centroidów (losowo, inspirowana KMeans++)
    def _initialize_centroids(self, data):
        if self.random_state is not None:
            np.random.seed(self.random_state)

        n_samples, n_features = data.shape
        centroids = np.zeros((self.n_clusters, n_features))
        centroids[0] = data[np.random.choice(n_samples)]  # pierwszy centroid losowo

        for k in range(1, self.n_clusters):
            distances_matrix = np.sqrt(np.sum((data[:, np.newaxis, :] - centroids[:k]) ** 2, axis=2))
            min_distances = np.min(distances_matrix ** 2, axis=1)

            # Im dalej punkt od istniejących centroidów, tym większa szansa na jego wybór
            probabilities = min_distances / np.sum(min_distances) if np.sum(min_distances) != 0 else np.ones_like(min_distances) / len(min_distances)
            centroids[k] = data[np.random.choice(n_samples, p=probabilities)]

        return centroids

    # Przypisanie punktów do najbliższego centroidu
    def _assign_to_clusters(self, data):
        assignments = np.zeros(data.shape[0], dtype=int)
        for i, point in enumerate(data):
            distances = self._euclidean_distance(point, self.centroids)
            assignments[i] = np.argmin(distances)
        return assignments

    # Aktualizacja centroidów jako średnich punktów w klastrze
    def _update_centroids(self, data, cluster_assignments):
        new_centroids = np.zeros_like(self.centroids)
        for i in range(self.n_clusters):
            points = data[cluster_assignments == i]
            if len(points) > 0:
                new_centroids[i] = np.mean(points, axis=0)
            else:
                new_centroids[i] = self.centroids[i]  # centroid zostaje jeśli nie ma punktów
        return new_centroids

    # 🔹 (e) Obliczanie bezwładności - suma odległości punktów od centroidów
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

            # 🔹 (d) Sprawdzenie warunku stopu - jeśli centroidy przesuwają się o mniej niż tol, algorytm się zatrzymuje
            movement = np.sum(np.linalg.norm(self.centroids - old_centroids, axis=1))
            if movement < self.tol:
                break

        # 🔹 (e) Obliczenie bezwładności po zakończeniu iteracji
        self.inertia = self._calculate_inertia(data, self.cluster_assignments)
        return self

    # Przypisanie nowych danych do istniejących centroidów
    def predict(self, data):
        return self._assign_to_clusters(data)


# ==========================
# Uruchomienie prób KMeans
# ==========================
def run_k_means_trials(data, labels, n_clusters, num_trials=5):
    best_model = None
    min_inertia = float('inf')

    for trial in range(num_trials):
        model = KMeans(n_clusters=n_clusters, max_iter=300, tol=1e-4, random_state=trial)
        model.fit(data)

        # 🔹 Wybór najlepszego modelu - wybieramy ten z najniższą bezwładnością
        if model.inertia < min_inertia:
            best_model = model
            min_inertia = model.inertia

    print(f"K={n_clusters} - Best inertia: {min_inertia:.2f}")
    
    # Wizualizacja wyników najlepszego modelu
    plot_cluster_assignment_matrix(y_true=labels, y_pred=best_model.cluster_assignments, n_clusters=n_clusters, title=f"Digit-cluster assignment (K={n_clusters})")
    visualize_clusters(best_model.centroids, f"Centroids (K={n_clusters})")
    return best_model
