import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Funkcja sigmoid przekształca dowolną liczbę rzeczywistą do zakresu (0, 1).
# Jest często używana do klasyfikacji binarnej, bo zachowuje się jak prawdopodobieństwo.
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# Pochodna funkcji sigmoid potrzebna do obliczania gradientu podczas uczenia.
def sigmoid_prime(x):
    s = sigmoid(x)
    return s * (1 - s)

# Funkcja ReLU zwraca wartość 0 dla argumentów ujemnych, a dla dodatnich przepuszcza je bez zmian.
# ReLU jest powszechnie stosowana w warstwach ukrytych nowoczesnych sieci neuronowych.
def relu(x):
    return np.maximum(0, x)

# Pochodna funkcji ReLU - 1 dla wartości dodatnich, 0 dla ujemnych.
def relu_prime(x):
    return (np.array(x) > 0).astype(float)

# Normalizacja L1 - dzieli każdy wektor przez sumę wartości bezwzględnych jego elementów.
# Powoduje, że suma wartości bezwzględnych elementów wektora wynosi 1.
def normalize_L1(X):
    norm = np.sum(np.abs(X), axis=0, keepdims=True)
    return X / (norm + 1e-8)

# Normalizacja L2 - dzieli każdy wektor przez jego długość euklidesową.
# Powoduje, że długość (norma) wektora wynosi 1.
def normalize_L2(X):
    norm = np.sqrt(np.sum(X**2, axis=0, keepdims=True))
    return X / (norm + 1e-8)

# Implementacja sieci neuronowej z jedną warstwą ukrytą.
class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size, activation_h_name='sigmoid', activation_o_name='sigmoid'):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        # Inicjalizacja wag i biasów małymi losowymi liczbami.
        self.W_ih = np.random.randn(self.hidden_size, self.input_size) * 0.01
        self.b_h = np.zeros((self.hidden_size, 1))

        self.W_ho = np.random.randn(self.output_size, self.hidden_size) * 0.01
        self.b_o = np.zeros((self.output_size, 1))

        # Wybór funkcji aktywacji
        self._set_activation_functions(activation_h_name, activation_o_name)

    def _set_activation_functions(self, activation_h_name, activation_o_name):
        if activation_h_name == 'sigmoid':
            self.activation_h = sigmoid
            self.activation_h_prime = sigmoid_prime
        elif activation_h_name == 'relu':
            self.activation_h = relu
            self.activation_h_prime = relu_prime
        else:
            raise ValueError(f"Błąd: nieznana funkcja aktywacji: '{activation_h_name}'")

        if activation_o_name == 'sigmoid':
            self.activation_o = sigmoid
            self.activation_o_prime = sigmoid_prime
        elif activation_o_name == 'relu':
            self.activation_o = relu
            self.activation_o_prime = relu_prime
        else:
            raise ValueError(f"Błąd: nieznana funkcja aktywacji: '{activation_o_name}'")

    # Propagacja w przód - obliczanie wyjścia sieci neuronowej.
    def forward(self, X):
        self.Z_h = np.dot(self.W_ih, X) + self.b_h
        self.A_h = self.activation_h(self.Z_h)

        self.Z_o = np.dot(self.W_ho, self.A_h) + self.b_o
        self.y_pred = self.activation_o(self.Z_o)
        return self.y_pred

    # Propagacja wsteczna - obliczanie gradientów i aktualizacja wag.
    def backward(self, X, y_true, learning_rate):
        num_examples = X.shape[1]
        d_loss_d_y_pred = self.y_pred - y_true
        delta_o = d_loss_d_y_pred * self.activation_o_prime(self.Z_o)

        d_W_ho = np.dot(delta_o, self.A_h.T)
        d_b_o = np.sum(delta_o, axis=1, keepdims=True)

        error_h = np.dot(self.W_ho.T, delta_o)
        delta_h = error_h * self.activation_h_prime(self.Z_h)

        d_W_ih = np.dot(delta_h, X.T)
        d_b_h = np.sum(delta_h, axis=1, keepdims=True)

        # Aktualizacja wag i biasów
        self.W_ho -= learning_rate * d_W_ho
        self.b_o -= learning_rate * d_b_o
        self.W_ih -= learning_rate * d_W_ih
        self.b_h -= learning_rate * d_b_h

    # Proces uczenia sieci neuronowej.
    def train(self, X_train, y_train, epochs, learning_rate, batch_size=None):
        num_samples = X_train.shape[1]
        X_train_processed = X_train.copy()

        if batch_size is None or batch_size >= num_samples:
            current_batch_size = num_samples
            print(f"Tryb: Pełny Batch Gradient Descent, rozmiar partii: {current_batch_size}.")
        else:
            current_batch_size = batch_size
            print(f"Tryb: Mini-Batch Gradient Descent, rozmiar partii: {current_batch_size}.")

        for epoch in range(epochs):
            permutation = np.random.permutation(num_samples)
            X_shuffled = X_train_processed[:, permutation]
            y_shuffled = y_train[:, permutation]

            epoch_loss = 0

            for i in range(0, num_samples, current_batch_size):
                X_batch = X_shuffled[:, i:i + current_batch_size]
                y_batch = y_shuffled[:, i:i + current_batch_size]

                y_pred = self.forward(X_batch)
                loss_batch = 0.5 * np.sum((y_pred - y_batch) ** 2)
                epoch_loss += loss_batch

                self.backward(X_batch, y_batch, learning_rate)

            avg_epoch_loss = epoch_loss / num_samples
            if (epoch + 1) % 100 == 0 or epoch == 0 or epoch == epochs - 1:
                print(f"Epoka {epoch + 1}/{epochs}, Strata: {avg_epoch_loss:.6f}")

    # Przewidywanie dla nowych danych.
    def predict(self, X_test):
        return self.forward(X_test.copy())

    # Obliczanie dokładności klasyfikacji.
    def calculate_accuracy(self, X_data, y_true):
        y_pred_raw = self.predict(X_data)
        predictions = (y_pred_raw >= 0.5).astype(int)
        accuracy = np.mean(predictions == y_true)
        return accuracy * 100

# Generowanie danych: dwie liczby, które mają ten sam lub różny znak.
def generate_same_sign_data(num_samples=2000, noise_std=0.05, include_zero_edge_cases=False):
    X = np.zeros((2, num_samples))
    y = np.zeros((1, num_samples))

    for i in range(num_samples):
        x1 = (np.random.rand() * 2) - 1
        x2 = (np.random.rand() * 2) - 1

        epsilon = 1e-6
        if abs(x1) < epsilon:
            x1 = np.random.choice([-1, 1]) * epsilon * 2
        if abs(x2) < epsilon:
            x2 = np.random.choice([-1, 1]) * epsilon * 2

        if (x1 > 0 and x2 > 0) or (x1 < 0 and x2 < 0):
            label = 1
        else:
            label = 0

        X[0, i] = x1
        X[1, i] = x2
        y[0, i] = label

    X += np.random.randn(2, num_samples) * noise_std

    return X, y
