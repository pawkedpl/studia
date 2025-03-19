#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <sys/random.h>
#include <time.h>

#define GROUPS 5

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


int partition_for_sort(int A[], int lo, int hi) {
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


void insertion_sort(int arr[], int low, int high) {
    for (int i = low + 1; i <= high; ++i) {
        int key = arr[i];
        int j = i - 1;
        while (j >= low && is_less(key, arr[j])) {
            arr[j + 1] = arr[j];
            j = j - 1;
        }
        arr[j + 1] = key;
    }
}


void sort(int A[], int lo, int hi) {
    if (lo >=0 && hi >= 0 && lo < hi) {
        int p;
        p = partition_for_sort(A, lo, hi);

        sort(A, lo, p);
        sort(A, p + 1, hi);
    }
 }

int partition(int arr[], int p, int q, int pivot) {
  int index;

  for(int i = p; i <= q; i++) {
    if(is_equal(pivot, arr[i])) {
      index = i;
      break;
    }
  }

  if(index != p)
    exchange(&arr[index], &arr[p]);

  index = p;
  int j = p;
  for(int i = p+1; i <= q; i++) {
    if(is_less(arr[i], arr[index])) {
      j++;
      exchange(&arr[j], &arr[i]);
    }
  }

  exchange(&arr[j], &arr[p]);
  return j;
}


int select_algorithm(int A[], int p, int q, int i) {
  if (p == q) {
    if (should_print) {
        printf("Jednoelementowa podtablica z: %d\n", A[p]);
    }

    return A[p];
  }


  int number_of_groups = ( ((q-p+1) % GROUPS == 0) ? ((q-p+1) / GROUPS): (((q-p+1)/GROUPS)+1) );
  int medians[number_of_groups];
  int index = 0;

  for (int i = p; i <= q; i += 5) {   
    if(i + (GROUPS - 1) <= q) {
      insertion_sort(A, i, i+ (GROUPS - 1));
      medians[index] = A[i+2];
      index++;
    }
    else {
      insertion_sort(A, i, q);
      medians[index] = A[i + ((q-i)/2)];
    }
  }

  int median_of_medians = select_algorithm(medians, 0, number_of_groups-1, ((number_of_groups + 1)/2));
  int r = partition(A, p, q, median_of_medians);
  int k = r - p + 1;

  if (should_print) {
      printf("Obecna mediana median: %d\n", A[r]);
  } 
  
  if (k == i) {
      return A[r];
  } else if (i < k) {
      return select_algorithm(A, p, r-1, i);
  } else {
      return select_algorithm(A, r+1, q, i-k);
  } 
}

bool is_ok(int A[], int stat, int value) {
    if (A[stat - 1] == value) {
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

    int A[length];
    int Init[length];

    for (int i = 0; i < length; i++) {
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
    struct timespec start, end;
    clock_gettime(CLOCK_REALTIME, &start);
    int value = select_algorithm(A, 0, length - 1, stat); //czy jest git??
    clock_gettime(CLOCK_REALTIME, &end);
    double t_ns = (double)(end.tv_sec - start.tv_sec) * 1.0e9 + (double)(end.tv_nsec - start.tv_nsec);


    if (should_print) {
        printf("Tablica poczatkowa:\n");
        for (int k = 0; k < length; k++) {
            if(Init[k]/10 < 1) {
                printf("0%d ", Init[k]);
            } else {
                printf("%d ", Init[k]);
            }
        }
        printf("\n");

        printf("Tablica po znalezieniu statystyki:\n");
        for (int k = 0; k < length; k++) {
            if(A[k]/10 < 1) {
                printf("0%d ", A[k]);
            } else {
                printf("%d ", A[k]);
            }
        }
        printf("\n");

        printf("Znalezniona statystyka: %d\n", value);

        printf("Posortowana tablica:\n");
        sort(A, 0, length - 1);
        for (int k = 0; k < length; k++) {
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
    printf("Czas dzialania: %f\n", t_ns);

    if (is_ok(A, stat, value)) {
        printf("Znaleziono prawidlowa statystyka.");
    } else {
        printf("Bledna statystyka.");
    }

    return 0;
}
