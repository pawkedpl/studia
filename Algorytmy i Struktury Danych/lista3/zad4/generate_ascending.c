#include <stdlib.h>
#include <stdio.h>
#include <sys/random.h>
#include <time.h>

int main(int argc, char *argv[]) {
    int length = atoi(argv[1]);
    int index = atoi(argv[2]);
    int tab[length];

    for (int i = 0; i < length; i++) {
        tab[i] = i + 1;
    }

    printf("%d\n", length);
    printf("%d\n", index);
    for (int i = 0; i < length; i++) {
        printf("%d\n", tab[i]);
    }

    return 0;
}
