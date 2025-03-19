#ifndef KRUSKAL_H
#define KRUSKAL_H

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <float.h>
#include <inttypes.h>

typedef struct Edge {
    long long u;
    long long v;
    double weight;
} Edge;

int cmp(const void *a, const void *b) {
    double res = ((Edge *)a)->weight - ((Edge *)b)->weight;
    return (res > 0) - (res < 0); //sprytne!
}

long long find(long long belongs[], long long i) {
    if (belongs[i] != i) {
        belongs[i] = find(belongs, belongs[i]);
    }

    return belongs[i];
}

void unionSets(long long belongs[], long long rank[], long long x, long long y) {
    long long rootX = find(belongs, x);
    long long rootY = find(belongs, y);

    if (rank[rootX] < rank[rootY]) {
        belongs[rootX] = rootY;
    } else if (rank[rootX] > rank[rootY]) {
        belongs[rootY] = rootX;
    } else {
        belongs[rootY] = rootX;
        rank[rootX]++;
    }
}

void kruskalMST(long long size, double **G) {
    long long *belongs = (long long *)malloc(size * sizeof(long long));
    long long *rank = (long long *)malloc(size * sizeof(long long));
    Edge *edges = (Edge *)malloc(size * size * sizeof(Edge));
    long long ind = 0;

    for (long long i = 0; i < size; i++) {
        for (long long j = 0; j < i; j++) {
            if (G[i][j] != 0) {
                edges[ind].u = i;
                edges[ind].v = j;
                edges[ind].weight = G[i][j];
                ind++;
            }
        }
    }

    qsort(edges, ind, sizeof(Edge), cmp);

    for (long long i = 0; i < size; i++) {
        belongs[i] = i;
    }

    long long ind_new = 0;
    Edge *mst = (Edge *)malloc(size * sizeof(Edge));

    for (long long i = 0; i < ind; i++) {
        long long a = find(belongs, edges[i].u);
        long long b = find(belongs, edges[i].v);

        if (a != b) {
            mst[ind_new] = edges[i];
            ind_new++;
            unionSets(belongs, rank, a, b);
        }
    }

    // Wizualizacja końcowego minimalnego drzewa rozpinającego
    printf("Minimalne drzewo rozpinające (MST):\n");

    for (long long i = 0; i < ind_new; i++) {
        printf("Krawędź: %lld - %lld, Waga: %lf\n", mst[i].u, mst[i].v, mst[i].weight);
    }

    free(mst);
    free(edges);
    free(rank);
    free(belongs);
}

#endif
