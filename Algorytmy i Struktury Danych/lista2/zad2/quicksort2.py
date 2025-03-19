import random
import sys


def quicksort(A, lo, hi):
  if lo >= 0 and hi >= 0 and lo < hi:
    (comp, swap, p) = partition(A, lo, hi)
    (lcomp, lswap) = quicksort(A, lo, p)
    (rcomp, rswap) = quicksort(A, p + 1, hi)
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
    

k_values = [1, 10, 20]
def generate_random_data(n):
    return random.sample(range(2 * n), n)
with open("wyniki_quicksort2.txt", "w") as file:
    for i in range(1000,50001,1000):
        n = i
        for k in k_values:
            j=0
            totalswaps=0
            totalcompa=0
            avswaps=0
            avcompa=0
            while(j<k):
                data_generator = generate_random_data
                y=data_generator(n)
                fullcomp, fullswaps = quicksort(y, 0, len(y) - 1)
                totalswaps+=fullswaps
                totalcompa+=fullcomp
                j+=1
            avcompa=int(totalcompa/k)
            avswaps=int(totalswaps/k)
            print("n=",i,"[", fullcomp, ",",fullswaps,"]")
            file.write("{},{},{},{}\n".format(i,k,avcompa, avswaps))
    






