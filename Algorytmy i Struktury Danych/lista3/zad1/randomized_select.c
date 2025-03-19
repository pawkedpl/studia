#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <sys/random.h>
#include <time.h>

int comp = 0;
int swap = 0;
bool should_print = false;

bool is_less(int a, int b) {
    comp++;

    if (a < b) {
        return true;
    } else {
        return false;
    }
}

bool is_equal(int a, int b) {
    comp++;

    if (a == b) {
        return true;
    } else {
        return false;
    }
}

bool is_less_equal(int a, int b) {
    comp++;
    
    if (a <= b) {
        return true;
    } else {
        return false;
    }
}

void exchange(int* a, int* b) {
    swap++;
    int temp = *a;
    *a = *b;
    *b = temp;
}



int partition(int A[], int lo, int hi) {
    int pivot = A[lo];
    int i = lo - 1;
    int j = hi + 1;

    while (true) {
        do {
            i++;
        } while(A[i] < pivot);

        do {
            j--;
        } while (pivot < A[j]);

        if (i >= j) {
            return j;
        }

        int temp = A[i];
        A[i] = A[j];
        A[j] = temp;
    }
}


void sort(int A[], int lo, int hi ) {
    if (lo >=0 && hi >= 0 && lo < hi) {
        int p = partition(A, lo, hi);
        
        sort(A, lo, p );
        sort(A, p + 1, hi);
    }
 }

int partition_count(int A[], int lo, int hi) {
    int pivot = A[lo];
    int i = lo - 1;
    int j = hi + 1;

    while (true) {
        do {
            i++;
        } while(is_less(A[i], pivot));

        do {
            j--;
        } while (is_less(pivot, A[j]));

        if (i >= j) {
            return j;
        }

        exchange(&A[i], &A[j]);
    }
}


int rand_partition(int A[], int p, int q) {
    unsigned int seed;
    getrandom(&seed, sizeof(seed), 0);
    srandom(seed);
    int r = (p + random() % (q - p));
    exchange(&A[p], &A[r]);
    return partition_count(A, p, q);
}


int select_algorithm(int A[], int p, int r, int i) {
    if (is_equal(p, r)) {
        if (should_print) {
            printf("Podtablica ma tylko jeden element: %d\n", A[p]);
        }

        return A[p];
    }

    int q = rand_partition(A, p, r);
    int k = q - p + 1;

    if (should_print) {
        printf("Wybrano pivot: %d\n", A[q]);
    }

    if (is_less_equal(i, k)) {
        return select_algorithm(A, p, q, i);
    } else {
        return select_algorithm(A, q + 1, r, i - k);
    }
}

bool is_ok(int A[], int stat, int value) {
    if (A[stat] == value) {
        return true;
    } else {
        return false;
    }
}


int main() {
    printf("Podaj dlugosc tablicy: \n");
    int length;
    scanf("%d", &length);

    printf("Podaj numer szukanej statystyki pozycyjnej: \n");
    int stat;
    scanf("%d", &stat);

    if (stat > length || stat < 1) {
        printf("Podano nieistniejaca statystyke pozycyjna");
        return 0;
    }

    printf("Podawaj wartosci tablicy: \n");

    int A[length+1];
    int Init[length+1];

    for (int i = 1; i < length+1; i++) {
        int num;
        scanf("%d", &num);
        A[i] = num;
        Init[i] = num;
    }

    if (length < 50) {
        should_print = true;
    }

    if (should_print) {
        printf("\n");
        printf("Kluczowe momenty:\n");
    }
    
    //właściwy algorytm
    int value = select_algorithm(A, 1, length, stat); //czy jest git??

    if (should_print) {
        printf("Tablica poczatkowa:\n");
        for (int k = 1; k < length+1; k++) {
            if(Init[k]/10 < 1) {
                printf("0%d ", Init[k]);
            } else {
                printf("%d ", Init[k]);
            }
        }
        printf("\n");

        printf("Tablica po znalezieniu statystyki:\n");
        for (int k = 1; k < length+1; k++) {
            if(A[k]/10 < 1) {
                printf("0%d ", A[k]);
            } else {
                printf("%d ", A[k]);
            }
        }
        printf("\n");

        printf("Znalezniona statystyka: %d\n", value);
    
        printf("Posortowana tablica:\n");
        sort(A, 1, length);
        for (int k = 1; k < length+1; k++) {
            if(A[k]/10 < 1) {
                printf("0%d ", A[k]);
            } else {
                printf("%d ", A[k]);
            }
        }
        printf("\n");
    }

    printf("Łączna liczba porównan między kluczami: %d\n", comp);
    printf("Łączna liczba przestawień kluczy: %d\n", swap);

    if (is_ok(A, stat, value)) {
        printf("Znaleziono prawidlowa statystyka.");
    } else {
        printf("Bledna statystyka.");
    }

    return 0;
}
