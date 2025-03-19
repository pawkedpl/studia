#ifndef KRUSKAL_H
#define KRUSKAL_H

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <float.h>
#include <inttypes.h>

typedef struct Edge {
    uint64_t u;
    uint64_t v;
    double weight;
} Edge;

//https://en.cppreference.com/w/c/algorithm/qsort
int cmp(const void *a, const void *b) {
    double res = ((Edge *)a)->weight - ((Edge *)b)->weight;
    return (res > 0) -  (res < 0); //sprytne!
}

uint64_t find(uint64_t belongs[], uint64_t i) {
    if (belongs[i] != i) {
        belongs[i] = find(belongs, belongs[i]);
    }

    return belongs[i];
}

void unionSets(uint64_t belongs[], uint64_t rank[], uint64_t x, uint64_t y) {
    uint64_t rootX = find(belongs, x);
    uint64_t rootY = find(belongs, y);

    if (rank[rootX] < rank[rootY]) {
        belongs[rootX] = rootY;
    } else if (rank[rootX] > rank[rootY]) {
        belongs[rootY] = rootX;
    } else {
        belongs[rootY] = rootX;
        rank[rootX]++;
    }
}

void kruskalMST(uint64_t size, double **G) {

    uint64_t *belongs = (uint64_t *)malloc(size *sizeof(uint64_t));
    uint64_t *rank = (uint64_t *)malloc(size *sizeof(uint64_t));
    Edge *edges = (Edge *)malloc(size *size *sizeof(Edge));
    uint64_t ind = 0;

    for (uint64_t i = 0; i < size; i++) {
        for (uint64_t j = 0; j < i; j++) {
            if (G[i][j] != 0) {
                edges[ind].u = i;
                edges[ind].v = j;
                edges[ind].weight = G[i][j];
                ind++;
            }
        }
    }

    qsort(edges, ind, sizeof(Edge), cmp);

    for (uint64_t i = 0; i < size; i++) {
        belongs[i] = i;
    }

    uint64_t ind_new = 0;
    Edge *mst = (Edge *)malloc(size *sizeof(Edge));

    for (uint64_t i = 0; i < ind; i++) {
        uint64_t a = find(belongs, edges[i].u);
        uint64_t b = find(belongs, edges[i].v);

        if (a != b) {
            mst[ind_new] = edges[i];
            ind_new++;

            unionSets(belongs, rank, a, b);
        }
    }

    free(mst);
    free(edges);
    free(rank);
    free(belongs);
}

#endif
