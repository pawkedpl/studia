#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <sys/random.h>
#include <time.h>

#define COMMAND_LEN 50
#define DATA_SIZE 2048
#define K_MAX 100

void results(char generator_type[30], char sort_type[20], int n, int index) {
    FILE *pf;
    char command[COMMAND_LEN];
    char data[DATA_SIZE];

    sprintf(command, "%s %d %d | %s", generator_type, n, index, sort_type);
    pf = popen(command, "r");

    if(!pf) {
        fprintf(stderr, "Nie otwarto rury.\n");
        return;
    }
    
   while (fgets(data, DATA_SIZE, pf) != NULL) {
        fprintf(stdout, "%s", data);
        fflush(stdout); 
    }

   if (pclose(pf) != 0) {
        fprintf(stderr, "Nie zamknieto streamu\n");
        }
}

int main() {



   for (int n = 1000; n <= 100000; n = n + 1000) {

        int index;
        // index = n + 1;  // nie ma w tablicy
        // index = n;      // jest na koncu
        // index = n/3;    // jest okolo na srodku
        // index = n/8;    // jest gdzies na poczatku
        unsigned int seed;
        getrandom(&seed, sizeof(seed), 0);
        srandom(seed);


        for (int k = 0; k < K_MAX; k++) {
            printf("%d ", n);
            index = (random() % n);
            results("./generate_ascending", "./binary_search", n, index);
            printf("\n");
        }
    }

   return 0;
}
