import matplotlib.pyplot as plt
import numpy as np


def read_data(filename):
    data = np.loadtxt(filename, delimiter=',', skiprows=0)
    return data

def generate_plots(algorithm, k_values):
    for k in k_values:
        
        filename = f"wyniki_{algorithm}.txt"
        data = read_data(filename)
        data_k = data[data[:, 1] == k]
        n_values = data_k[:, 0]
        avg_comparisons = data_k[:, 2]
        avg_swaps = data_k[:, 3]
        ratio_comparisons = avg_comparisons / n_values
        ratio_swaps = avg_swaps / n_values
        plt.figure(figsize=(12, 8))
        plt.subplot(2, 2, 1)
        plt.plot(n_values, avg_comparisons, label=f'k={k}')
        plt.title(f'Average Comparisons ({algorithm})')
        plt.xlabel('n')
        plt.ylabel('Average Comparisons')
        plt.legend()

        
        plt.subplot(2, 2, 2)
        plt.plot(n_values, avg_swaps, label=f'k={k}')
        plt.title(f'Average Swaps ({algorithm})')
        plt.xlabel('n')
        plt.legend()

        
        plt.subplot(2, 2, 3)
        plt.plot(n_values, ratio_comparisons, label=f'k={k}')
        plt.title(f'comparisions/n ({algorithm})')
        plt.xlabel('n')
        plt.legend()

        
        plt.subplot(2, 2, 4)
        plt.plot(n_values, ratio_swaps, label=f'k={k}')
        plt.title(f'swaps/n ({algorithm})')
        plt.xlabel('n')
        plt.legend()

        plt.tight_layout()

        
        plt.savefig(f'{algorithm}_k{k}_plots.png')

        
        plt.show()

def main():
    algorithms = ['insertionsort', 'hybridsort', 'quicksort']
    k_values = [1, 10, 20]
    for algorithm in algorithms:
        generate_plots(algorithm, k_values)

if __name__ == "__main__":
    main()
