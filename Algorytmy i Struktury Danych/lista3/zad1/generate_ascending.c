#include <stdlib.h>
#include <stdio.h>
#include <sys/random.h>
#include <time.h>

int main(int argc, char *argv[]) {
    int length = atoi(argv[1]);
    int tab[length];

    for (int i = 0; i < length; i++) {
        tab[i] = i + 1;
    }

    unsigned int seed;
    getrandom(&seed, sizeof(seed), 0);
    srandom(seed);
    int random_index = (1 + random() % (length));

    printf("%d\n", length);
    printf("%d\n", random_index);
    for (int i = 0; i < length; i++) {
        printf("%d\n", tab[i]);
    }

    return 0;
}
