import random
import sys


zamiany = 0
porownania = 0


def insertion_sort(arr):
    global zamiany, porownania
    zamiany, porownania = 0, 0
    n = len(arr)
    for i in range(1, n):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
            zamiany += 1
            porownania += 1
            if n < 40:  
                print(" ".join(f"{x:02d}" for x in arr))
        arr[j + 1] = key
        porownania += 1


def generate_random_data(n):
    return [random.randint(0, 2*n - 1) for _ in range(n)]


def generate_ascending_data(n):
    return list(range(n))


def generate_descending_data(n):
    return list(range(n, 0, -1))


def test_and_print(data_generator, n):
    global zamiany, porownania
   
    data = data_generator(n)
    
    input_data = data[:]
   
    print("Input array:")
    print(" ".join(f"{x:02d}" for x in data))
    print()
   
    insertion_sort(data)
    
    print("Sorted array:")
    print(" ".join(f"{x:02d}" for x in data))
    print()
    
    if data == sorted(input_data):
        print("Array is sorted correctly.")
    else:
        print("Error! Array is not sorted correctly.")
    
    print("Number of comparisons:", porownania)
    print("Number of swaps:", zamiany)



if len(sys.argv) != 3:
    print("Usage: data_generator n | sorting_program")
    sys.exit(1)

generator_type = sys.argv[1]
n = int(sys.argv[2])

if generator_type == "random":
    data_generator = generate_random_data
elif generator_type == "ascending":
    data_generator = generate_ascending_data
elif generator_type == "descending":
    data_generator = generate_descending_data
else:
    print("Invalid data generator type.")
    sys.exit(1)

test_and_print(data_generator, n)
