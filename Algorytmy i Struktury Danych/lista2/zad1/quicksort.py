import random
import sys


def quicksort(A, lo, hi):
  if lo >= 0 and hi >= 0 and lo < hi:
    (comp, swap, p) = partition(A, lo, hi)
    (lcomp, lswap) = quicksort(A, lo, p)
    (rcomp, rswap) = quicksort(A, p + 1, hi)
    if(len(A) <40):
        print("Partitions: ", A[lo:p], A[p:hi+1])

    return comp + lcomp + rcomp, swap + lswap + rswap
  return (0,0)

def partition(A, lo, hi):
  comp = 0
  swap = 0
  pivot = A[(hi + lo) // 2]
  i = lo
  j = hi
  while True:
    while A[i] < pivot:
      comp += 1
      i += 1
    while A[j] > pivot:
      comp += 1
      j -= 1
    if i >= j:
      return (comp, swap, j)
    swap += 1
    A[i], A[j] = A[j], A[i]
    


def generate_random_data(n):
    return random.sample(range(2 * n), n)


def generate_ascending_data(n):
    return list(range(n))


def generate_descending_data(n):
    return list(range(n, 0, -1))


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


y=data_generator(n)
print("Start array:",y)
fullcomp, fullswaps = quicksort(y, 0, len(y) - 1)
print("Sorted array:", y)
print("Total comparisons:", fullcomp)
print("Total swaps:", fullswaps)


