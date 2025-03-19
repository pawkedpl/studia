#ifndef GENERATE_GRAPH_H
#define GENERATE_GRAPH_H

#include <sys/random.h>
#include <time.h>
#include <stdlib.h>
#include <inttypes.h>

void make_graph(long long size, double **G) {

    unsigned int seed;
    getrandom( &seed, sizeof(seed), 0);
    srandom(seed);

    for (long long i = 0; i < size; i++) {
        for (long long j = i + 1; j < size; j++) {
            double rand_weight = (double)random() / (double)((unsigned)RAND_MAX + 1);

            G[i][j] = rand_weight;
            G[j][i] = rand_weight;
        }

        G[i][i] = 0.0;
    }
}

#endif
