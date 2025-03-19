import random


def insertion_sort(arr):
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
            
        arr[j + 1] = key
        porownania += 1
    return porownania, zamiany
    


def generate_random_data(n):
    return [random.randint(0, 2*n - 1) for _ in range(n)]

k_values = [1, 10, 20]
with open("wyniki_insertionsort.txt", "w") as file:
    for i in range(10,51,10):
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
                fullcomp, fullswaps = insertion_sort(y)
                totalswaps+=fullswaps
                totalcompa+=fullcomp
                j+=1
            avcompa=int(totalcompa/k)
            avswaps=int(totalswaps/k)
            print("n=",i,"[", fullcomp, ",",fullswaps,"]")
            file.write("{},{},{},{}\n".format(i,k,avcompa, avswaps))
