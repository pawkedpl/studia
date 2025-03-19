#ifndef PRIM_H
#define PRIM_H

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <float.h>
#include <inttypes.h>

uint64_t min(uint64_t size, double key[], bool mst[]) {
    double min = DBL_MAX;
    uint64_t min_index = 0;

    for (uint64_t i = 0; i < size; i++)  {
        if (mst[i] == false && key[i] < min) {
            min = key[i];
            min_index = i;
        }
    }

    return min_index;
}

void primMST(uint64_t size, double **G) {
    // tutaj trzymam MST
    uint64_t *parent = (uint64_t *)malloc(size *sizeof(uint64_t));

    // do brania minimalnej wagi (zachlannie)
    double *key = (double *)malloc(size *sizeof(double));


    // te wziete do MST
    bool *mst = (bool *)malloc(size *sizeof(bool));


    for (uint64_t i = 0; i < size; i++) {
        key[i] = DBL_MAX; //jako infinity
        mst[i] = false;
    }

    // biore pierwszy wierzcholek
    key[0] = 0.0;
    parent[0] = -1; //jako root

    for (uint64_t i = 0; i < size - 1; i++) {
        uint64_t u = min(size, key, mst);
        mst[u] = true;

        for (uint64_t j = 0; j < size; j++) {
            if (G[u][j] && mst[j] == false && G[u][j] < key[j] ) {
                parent[j] = u;
                key[j] = G[u][j];
            }
        }

    }

    free(parent);
    free(key);
    free(mst);
}

#endif
