import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# %% [markdown]
# ## Functions

# %% [markdown]
# ### Sigmoid
# 
# The **sigmoid function** is an S-shaped curve that maps any real-valued number to a value between 0 and 1, often used for binary classification output or as an activation function in neural networks.
# $$f(x) = \frac{1}{1+e^{-x}}$$
# $$f'(x) = f(x)(1-f(x))$$

# %%
def sigmoid(x):
    return 1 / (1 + np.exp(-x)) 

def sigmoid_prime(x):
    s = sigmoid(x)
    return s * (1 - s)

# %% [markdown]
# ### ReLU
# 
# The **ReLU (Rectified Linear Unit) function** outputs the input directly if it's positive, otherwise it outputs zero. It's widely used in hidden layers of neural networks for its computational efficiency and ability to mitigate vanishing gradients.
# 
# $$f(x) = max(0,x)$$
# $$f'(x) = \begin{cases} 1 \ for\ x > 0 \\ 0 \ for\ x \leq 0 \end{cases}$$

# %%
def relu(x):
    return np.maximum(0, x)

def relu_prime(x):
    return (np.array(x) > 0).astype(float)

# %% [markdown]
# ### L1 Norm (Manhattan)
# 
# L1 Norm (Manhattan distance or Taxicab norm) is a measure of vector magnitude calculated as the sum of the absolute values of its components. It's often used in machine learning for feature selection (Lasso regularization) as it can lead to sparse solutions.
# 
# $$\|X\|_1 = |x_1|+|x_2|$$
# $$X_{norm} = \left[\frac{x_1}{|x_1|+|x_2|},\frac{x_2}{|x_1|+|x_2|}\right]$$

# %%
def normalize_L1(X):
    norm = np.sum(np.abs(X), axis=0, keepdims=True)
    return X / (norm + 1e-8)

# %% [markdown]
# ### L2 Norm (Euclidean)
# 
# L2 Norm (Euclidean norm) is a measure of vector magnitude calculated as the square root of the sum of the squared values of its components. It's commonly used in machine learning for regularization (Ridge regularization) to prevent overfitting by penalizing large weights.
# 
# $$\|X\|_2 = \sqrt{x_1^2+x_2^2}$$
# $$X_{norm} = \left[\frac{x_1}{\sqrt{x_1^2+x_2^2}},\frac{x_2}{\sqrt{x_1^2+x_2^2}}\right]$$

# %%
def normalize_L2(X):
    norm = np.sqrt(np.sum(X**2, axis=0, keepdims=True))
    return X / (norm + 1e-8)

# %% [markdown]
# ## Neural Network Model
# 
# 
# | Variables | Description               |
# |----------|---------------------------|
# | $I$      | number of input features  |
# | $H$      | number of hidden layer neurons |
# | $O$      | number of output layer neurons |
# | $N$      | number of samples in the batch |
# 
# 
# ### Forward Pass
# 
# | Symbol | Description               |
# |----------|---------------------------|
# | $X$      | input data                |
# | $W_{ih}$ | input-to-hidden weights   |
# | $b_h$    | hidden layer biases       |
# | $W_{ho}$ | hidden-to-output weights  |
# | $b_o$    | output layer biases       |
# | $f_h$    | hidden layer activation function |
# | $f_o$    | output layer activation function |
# 
# 
# 1. Calculations for the Hidden Layer:
# $$Z_h = W_{ih} X + b_h$$
# $$A_h = f_h(Z_h)$$
# 
# 2. Calculations for the Output Layer:
# $$Z_o = W_{ho} A_h + b_o$$
# $$y_{\text{pred}} = f_o(Z_o)$$
# 
# 
# 
# 
# 

# %% [markdown]
# ### Backpropagation
# 
# The `backward` method computes the gradients of the loss function with respect to the weights and biases, and then updates them to minimize the network's error. This process relies on the chain rule of calculus.
# 
# The network uses the **Mean Squared Error (MSE)** loss function, defined as:
# $$L = \frac{1}{2N} \sum_{k=1}^{N} (y_{\text{pred},k} - y_{\text{true},k})^2$$
# where $N$ is the number of samples in the batch, $y_{\text{pred},k}$ is the predicted output, and $y_{\text{true},k}$ is the true label for the $k$-th sample.
# 
# \subsection*{Symbols:}
# | Symbol | Description               |
# |----------|---------------------------|
# | $\alpha$ | learning rate             |
# | $N$      | number of samples in the batch |
# | $y_{\text{true}}$ | true labels        |
# | $y_{\text{pred}}$ | predicted outputs   |
# | $Z_o$    | weighted sum before output activation |
# | $A_h$    | hidden layer activations  |
# | $Z_h$    | weighted sum before hidden activation |
# | $\sigma'$ | derivative of activation function |
# | $\delta_o$ | error term for output layer |
# | $\delta_h$ | error term for hidden layer |
# 
# \textbf{Algorithm:}
# 
# 1.  **Output Layer Error ($\delta_o$):**
# 
#     The error of the output layer is the product of the loss function's derivative with respect to predictions and the derivative of the output layer's activation function with respect to its weighted sum of inputs ($Z_o$).
#     $$\delta_o = (y_{\text{pred}} - y_{\text{true}}) \odot f_o'(Z_o)$$
#     where $\odot$ denotes the Hadamard product (element-wise multiplication), and $f_o'$ is the derivative of the output activation function.
# 
# 2.  **Gradients for Output Layer Weights and Biases ($W_{ho}, b_o$):**
# 
#     Gradients for the weights and biases connecting the hidden layer to the output layer are calculated as:
#     $$\frac{\partial L}{\partial W_{ho}} = \frac{1}{N} \delta_o A_h^T$$
#     $$\frac{\partial L}{\partial b_o} = \frac{1}{N} \sum_{k=1}^{N} \delta_o^{(k)}$$
# 
# 3.  **Hidden Layer Error ($\delta_h$):**
# 
#     The hidden layer error is backpropagated from the output layer. It's the matrix product of the transposed output layer weights and the output layer error, followed by a Hadamard product with the derivative of the hidden layer's activation function.
#     $$\delta_h = (W_{ho}^T \delta_o) \odot f_h'(Z_h)$$
#     where $f_h'$ is the derivative of the hidden activation function.
# 
# 4.  **Gradients for Hidden Layer Weights and Biases ($W_{ih}, b_h$):**
# 
#     Gradients for the weights and biases connecting the input layer to the hidden layer are calculated as:
#     $$\frac{\partial L}{\partial W_{ih}} = \frac{1}{N} \delta_h X^T$$
#     $$\frac{\partial L}{\partial b_h} = \frac{1}{N} \sum_{k=1}^{N} \delta_h^{(k)}$$
# 
# 5.  **Updating Weights and Biases:**
# 
#     Weights and biases are updated in the opposite direction of the gradient, scaled by the learning rate ($\alpha$):
#     $$W_{\text{new}} = W_{\text{old}} - \alpha \frac{\partial L}{\partial W}$$
#     $$b_{\text{new}} = b_{\text{old}} - \alpha \frac{\partial L}{\partial b}$$

# %%
class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size, activation_h_name='sigmoid', activation_o_name='sigmoid'):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        self.W_ih = np.random.randn(self.hidden_size, self.input_size) * 0.01
        self.b_h = np.zeros((self.hidden_size, 1))

        self.W_ho = np.random.randn(self.output_size, self.hidden_size) * 0.01
        self.b_o = np.zeros((self.output_size, 1))

        self._set_activation_functions(activation_h_name, activation_o_name)

    def _set_activation_functions(self, activation_h_name, activation_o_name):

        if activation_h_name == 'sigmoid':
            self.activation_h = sigmoid
            self.activation_h_prime = sigmoid_prime
        elif activation_h_name == 'relu':
            self.activation_h = relu
            self.activation_h_prime = relu_prime
        else:
            raise ValueError(f"Error: Wrong function name: '{activation_h_name}'. " "Use 'sigmoid' or 'relu'.")

        if activation_o_name == 'sigmoid':
            self.activation_o = sigmoid
            self.activation_o_prime = sigmoid_prime
        elif activation_o_name == 'relu':
            self.activation_o = relu
            self.activation_o_prime = relu_prime
        else:
            raise ValueError(f"Error: Wrong function name: '{activation_o_name}'. " "Use 'sigmoid' or 'relu'.")

    def forward(self, X):
        self.Z_h = np.dot(self.W_ih, X) + self.b_h
        self.A_h = self.activation_h(self.Z_h)

        self.Z_o = np.dot(self.W_ho, self.A_h) + self.b_o
        self.y_pred = self.activation_o(self.Z_o)
        return self.y_pred

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
        
        self.W_ho   -= learning_rate * d_W_ho
        self.b_o    -= learning_rate * d_b_o
        self.W_ih   -= learning_rate * d_W_ih
        self.b_h    -= learning_rate * d_b_h
    def train(self, X_train, y_train, epochs, learning_rate, batch_size=None):
        num_samples = X_train.shape[1]
        X_train_processed = X_train.copy()

        if batch_size is None or batch_size >= num_samples:
            current_batch_size = num_samples
            print(f"Tryb treningu: Pełny Batch Gradient Descent (rozmiar partii: {current_batch_size}).")
        else:
            current_batch_size = batch_size
            print(f"Tryb treningu: Mini-Batch Gradient Descent (rozmiar partii: {current_batch_size}).")
        
        for epoch in range(epochs):
            permutation = np.random.permutation(num_samples)
            X_shuffled = X_train_processed[:, permutation]
            y_shuffled = y_train[:, permutation]

            epoch_loss = 0

            for i in range(0, num_samples, current_batch_size):
                X_batch = X_shuffled[:, i:i + current_batch_size]
                y_batch = y_shuffled[:, i:i + current_batch_size]

                y_pred = self.forward(X_batch)
                loss_batch = 0.5 * np.sum((y_pred - y_batch)**2)
                epoch_loss += loss_batch
                
                self.backward(X_batch, y_batch, learning_rate)
            avg_epoch_loss = epoch_loss / num_samples
            if (epoch + 1) % 100 == 0 or epoch == 0 or  epoch == epochs - 1:
                print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_epoch_loss:.6f}")

    def predict(self, X_test):
        return self.forward(X_test.copy())
    def calculate_accuracy(self, X_data, y_true):
        y_pred_raw = self.predict(X_data)

        predictions = (y_pred_raw >= 0.5).astype(int)
        accuracy = np.mean(predictions == y_true)
        return accuracy * 100



        

# %% [markdown]
# # Testing

# %% [markdown]
# ## Data generation function
# 

# %%
import numpy as np

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

# %% [markdown]
# ## Running Simulation

# %%
import numpy as np
import matplotlib.pyplot as plt


def run_simulation(X_train, y_train, X_test, y_test, activation_h_name, activation_o_name, title_prefix=""):

    INPUT_SIZE = 2
    HIDDEN_SIZE = 4
    OUTPUT_SIZE = 1

    EPOCHS = 3000 
    BATCH_SIZE = 32

    learning_rates_to_test = [0.1, 0.01, 0.001]

    simulation_results = {}
    trained_models = []

    activation_h_name = activation_h_name
    activation_o_name = activation_o_name

    for lr in learning_rates_to_test:
        print(f"\n--- Training: {title_prefix}, Activation: {activation_h_name}-{activation_o_name}, LR: {lr} ---")

        nn = NeuralNetwork(input_size=INPUT_SIZE, hidden_size=HIDDEN_SIZE, output_size=OUTPUT_SIZE,
                           activation_h_name=activation_h_name,
                           activation_o_name=activation_o_name)

        nn.train(X_train, y_train, epochs=EPOCHS, learning_rate=lr, batch_size=BATCH_SIZE)

        train_acc = nn.calculate_accuracy(X_train, y_train)
        test_acc = nn.calculate_accuracy(X_test, y_test)
        
        print(f"   Train accuracy: {train_acc:.2f}%")
        print(f"   Test  accuracy: {test_acc:.2f}%")
        
        simulation_results[lr] = {'train_accuracy': train_acc, 'test_accuracy': test_acc}
        trained_models.append(nn)

    return simulation_results



# %% [markdown]
# ### Data generation

# %%
np.random.seed(42)
NUM_SAMPLES = 1000
NOISE_STD = 0.03
X_raw, y_raw = generate_same_sign_data(num_samples=NUM_SAMPLES, noise_std=NOISE_STD, include_zero_edge_cases=True)


train_split = int(0.8 * X_raw.shape[1])
X_train_raw = X_raw[:, :train_split]
y_train     = y_raw[:, :train_split]
X_test_raw  = X_raw[:, train_split:]
y_test      = y_raw[:, train_split:]


all_experiment_results = {}

# %% [markdown]
# ### Data No Normalization

# %%
X_train_processed = X_train_raw.copy()
X_test_processed = X_test_raw.copy()

# %% [markdown]
# ### Experiment 1: No Normalization, Sigmoid_Sigmoid

# %%
norm_name = "No Normalization"
activation_h = 'sigmoid'
activation_o = 'sigmoid'

current_exp_results = run_simulation(
    X_train=X_train_processed, y_train=y_train,
    X_test=X_test_processed, y_test=y_test,
    activation_h_name=activation_h, activation_o_name=activation_o,
    title_prefix=f"{norm_name}, {activation_h}_{activation_o}"
)
for lr, res in current_exp_results.items():
    all_experiment_results[(norm_name, f"{activation_h}_{activation_o}", lr)] = res

# %% [markdown]
# ### Experiment 2: No Normalization, ReLU_Sigmoid

# %%
norm_name = "No Normalization"
activation_h = 'relu'
activation_o = 'sigmoid'

current_exp_results = run_simulation(
    X_train=X_train_processed, y_train=y_train,
    X_test=X_test_processed, y_test=y_test,
    activation_h_name=activation_h, activation_o_name=activation_o,
    title_prefix=f"{norm_name}, {activation_h}_{activation_o}"
)
for lr, res in current_exp_results.items():
    all_experiment_results[(norm_name, f"{activation_h}_{activation_o}", lr)] = res

# %% [markdown]
# ### Data L1 Normalization

# %%
X_train_processed   = normalize_L1(X_train_raw.copy())
X_test_processed    = normalize_L1(X_test_raw.copy())

# %% [markdown]
# ### Experiment 3: L1 Normalization, Sigmoid_Sigmoid

# %%
norm_name = "L1 Normalization"
activation_h = 'sigmoid'
activation_o = 'sigmoid'

current_exp_results = run_simulation(
    X_train=X_train_processed, y_train=y_train,
    X_test=X_test_processed, y_test=y_test,
    activation_h_name=activation_h, activation_o_name=activation_o,
    title_prefix=f"{norm_name}, {activation_h}_{activation_o}"
)
for lr, res in current_exp_results.items():
    all_experiment_results[(norm_name, f"{activation_h}_{activation_o}", lr)] = res

# %% [markdown]
# ### Experiment 4: L1 Normalization, ReLU_Sigmoid

# %%
print("\n##### Running Experiment 4: L1 Normalization, ReLU_Sigmoid #####")
norm_name = "L1 Normalization"
activation_h = 'relu'
activation_o = 'sigmoid'

current_exp_results = run_simulation(
    X_train=X_train_processed, y_train=y_train,
    X_test=X_test_processed, y_test=y_test,
    activation_h_name=activation_h, activation_o_name=activation_o,
    title_prefix=f"{norm_name}, {activation_h}_{activation_o}"
)
for lr, res in current_exp_results.items():
    all_experiment_results[(norm_name, f"{activation_h}_{activation_o}", lr)] = res

# %% [markdown]
# ### Data L2 Normalization

# %%
X_train_processed   = normalize_L2(X_train_raw.copy())
X_test_processed    = normalize_L2(X_test_raw.copy())

# %% [markdown]
# ### Experiment 5: L2 Normalization, Sigmoid_Sigmoid 

# %%
norm_name = "L2 Normalization"
activation_h = 'sigmoid'
activation_o = 'sigmoid'

current_exp_results = run_simulation(
    X_train=X_train_processed, y_train=y_train,
    X_test=X_test_processed, y_test=y_test,
    activation_h_name=activation_h, activation_o_name=activation_o,
    title_prefix=f"{norm_name}, {activation_h}_{activation_o}"
)
for lr, res in current_exp_results.items():
    all_experiment_results[(norm_name, f"{activation_h}_{activation_o}", lr)] = res

# %% [markdown]
# ### Experiment 6: L2 Normalization, ReLU_Sigmoid

# %%
norm_name = "L2 Normalization"
activation_h = 'relu'
activation_o = 'sigmoid'

current_exp_results = run_simulation(
    X_train=X_train_processed, y_train=y_train,
    X_test=X_test_processed, y_test=y_test,
    activation_h_name=activation_h, activation_o_name=activation_o,
    title_prefix=f"{norm_name}, {activation_h}_{activation_o}"
)
for lr, res in current_exp_results.items():
    all_experiment_results[(norm_name, f"{activation_h}_{activation_o}", lr)] = res

# %% [markdown]
# ## Results Comparison

# %%

results_list = []
for (norm_type, activation_config, lr), metrics in all_experiment_results.items():
    results_list.append({
        'Normalization': norm_type,
        'Activation': activation_config,
        'Learning Rate': lr,
        'Train Accuracy (%)': f"{metrics['train_accuracy']:.2f}",
        'Test Accuracy (%)': f"{metrics['test_accuracy']:.2f}"
    })

results_df = pd.DataFrame(results_list)

results_df_sorted = results_df.sort_values(by=['Normalization', 'Activation', 'Learning Rate'], ascending=[True, True, False])

print("### Summary of All Experiment Results")
print(results_df_sorted.to_markdown(index=False))


