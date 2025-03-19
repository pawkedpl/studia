import random
import matplotlib.pyplot as plt

def merge_sort_with_increasing_subsequences(arr):
    
    def merge(arr, start, mid, end):
        global comparisons_custom, swaps_custom
        left = arr[start:mid + 1]
        right = arr[mid + 1:end + 1]

        i, j, k = 0, 0, start

        while i < len(left) and j < len(right):
            comparisons_custom += 1
            if left[i] <= right[j]:
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
                swaps_custom += 1
            k += 1

        while i < len(left):
            arr[k] = left[i]
            i += 1
            k += 1

        while j < len(right):
            arr[k] = right[j]
            j += 1
            k += 1

   
    def find_increasing_subsequences(arr):
        sequences = []
        start = 0
        for i in range(1, len(arr)):
            if arr[i] < arr[i - 1]:
                sequences.append((start, i - 1))
                start = i
        sequences.append((start, len(arr) - 1))
        return sequences

    
    def merge_sort(arr, sequences):
        if len(sequences) <= 1:
            return
        merged_sequences = []
        for i in range(0, len(sequences), 2):
            if i + 1 < len(sequences):
                start1, end1 = sequences[i]
                start2, end2 = sequences[i + 1]
                merge(arr, start1, end1, end2)
                merged_sequences.append((start1, end2))
                print("Custom Merge Sort:", arr[start1:end2+1]) 
            else:
                merged_sequences.append(sequences[i])
        merge_sort(arr, merged_sequences)

    
    sequences = find_increasing_subsequences(arr)
   
    merge_sort(arr, sequences)
    print("Custom Merge Sort:", arr)
    

def merge_sort_classic(arr):
    global comparisons_merge, swaps_merge
    if len(arr) > 1:
        mid = len(arr) // 2
        left_half = arr[:mid]
        right_half = arr[mid:]

        merge_sort_classic(left_half)
        merge_sort_classic(right_half)

        i = j = k = 0

        while i < len(left_half) and j < len(right_half):
            comparisons_merge += 1
            if left_half[i] < right_half[j]:
                arr[k] = left_half[i]
                i += 1
            else:
                arr[k] = right_half[j]
                j += 1
                swaps_merge += 1
            k += 1

        while i < len(left_half):
            arr[k] = left_half[i]
            i += 1
            k += 1

        while j < len(right_half):
            arr[k] = right_half[j]
            j += 1
            k += 1
        
        print("Classic Merge Sort:", arr)

def generate_random_data(n):
    return [random.randint(0, 2*n - 1) for _ in range(n)]

def generate_ascending_data(n):
    return list(range(n))

def generate_descending_data(n):
    return list(range(n, 0, -1))

def plot_results(x, y_custom_comparisons, y_custom_swaps, y_merge_comparisons, y_merge_swaps):
    plt.plot(x, y_custom_comparisons, label='Custom Merge Comparisons', linestyle='--', color='blue')
    plt.plot(x, y_custom_swaps, label='Custom Merge Swaps', linestyle='-', color='blue')
    plt.plot(x, y_merge_comparisons, label='Classic Merge Comparisons', linestyle='--', color='red')
    plt.plot(x, y_merge_swaps, label='Classic Merge Swaps', linestyle='-', color='red')
    plt.xlabel('Size of Array')
    plt.ylabel('Number')
    plt.title('Custom MergeSort and Classic MergeSort')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    sizes = list(range(10, 51, 10))

    custom_comparisons = []
    custom_swaps = []
    merge_comparisons = []
    merge_swaps = []

    for size in sizes:
        data_random = generate_random_data(size)
        data_ascending = generate_ascending_data(size)
        data_descending = generate_descending_data(size)

        global comparisons_custom, swaps_custom, comparisons_merge, swaps_merge
        comparisons_custom = 0
        swaps_custom = 0
        comparisons_merge = 0
        swaps_merge = 0

        print("Size:", size)
        print("Random Data:")
        merge_sort_with_increasing_subsequences(data_random[:])
        merge_sort_classic(data_random[:])
        print("--------------------")

        custom_comparisons.append(comparisons_custom)
        custom_swaps.append(swaps_custom)
        merge_comparisons.append(comparisons_merge)
        merge_swaps.append(swaps_merge)

    plot_results(sizes, custom_comparisons, custom_swaps, merge_comparisons, merge_swaps)
