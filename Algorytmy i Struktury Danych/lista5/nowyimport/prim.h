#ifndef PRIM_H
#define PRIM_H

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <float.h>
#include <inttypes.h>

long long min(long long size, double key[], bool mst[]) {
    double min = DBL_MAX;
    long long min_index = 0;

    for (long long i = 0; i < size; i++)  {
        if (mst[i] == false && key[i] < min) {
            min = key[i];
            min_index = i;
        }
    }

    return min_index;
}

void primMST(long long size, double **G) {
    // tutaj trzymam MST
    long long *parent = (long long *)malloc(size * sizeof(long long));

    // do brania minimalnej wagi (zachlannie)
    double *key = (double *)malloc(size * sizeof(double));


    // te wziete do MST
    bool *mst = (bool *)malloc(size * sizeof(bool));


    for (long long i = 0; i < size; i++) {
        key[i] = DBL_MAX; //jako infinity
        mst[i] = false;
    }

    // biore pierwszy wierzcholek
    key[0] = 0.0;
    parent[0] = -1; //jako root

    for (long long i = 0; i < size - 1; i++) {
        long long u = min(size, key, mst);
        mst[u] = true;

        for (long long j = 0; j < size; j++) {
            if (G[u][j] && mst[j] == false && G[u][j] < key[j] ) {
                parent[j] = u;
                key[j] = G[u][j];
            }
        }

    }

// Wizualizacja końcowego minimalnego drzewa rozpinającego
    //printf("Minimalne drzewo rozpinające (MST) z algorytmu Prima:\n");
    //for (long long i = 1; i < size; i++) {
    //printf("Krawędź: %lld - %lld, Waga: %lf\n", parent[i], i, G[i][parent[i]]);
    //}

    free(parent);
    free(key);
    free(mst);
}

#endif
