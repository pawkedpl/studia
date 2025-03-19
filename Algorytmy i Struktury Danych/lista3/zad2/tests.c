#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>

#define COMMAND_LEN 50
#define DATA_SIZE 2048
#define K_MAX 50

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
   for (int n = 100; n <= 50000; n = n + 100) {

        int index;
        index = 1;
        // index = n;
        // index = n/2;
        // index = n/4;

        for (int k = 0; k < K_MAX; k++) {
            printf("%d ", n);
            results("./generate_random", "./randomized_select", n, index);
            results("./generate_random", "./select_five", n, index);
            printf("\n");
        }
    }
   return 0;
}
