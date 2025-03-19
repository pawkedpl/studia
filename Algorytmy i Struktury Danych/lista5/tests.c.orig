
#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <inttypes.h>
#include "prim.h"
#include "kruskal.h"
#include "generate_graph.h"

#define K_MAX 10

typedef struct results {
    double time_prime;
    double time_kruskal;
} results;


uint64_t timespec_diff_us(struct timespec *start, struct timespec *end) {
    return (end->tv_sec - start->tv_sec) * 1000000 +
           (end->tv_nsec - start->tv_nsec) / 1000;
}

int main() {
    int num_threads = omp_get_max_threads();
    omp_set_num_threads(num_threads);


    #pragma omp parallel for collapse(2) schedule(dynamic)

    for (int n = 1000; n <= 10000; n += 1000) {
        for (int k = 1; k < K_MAX; k++) {

            double **graph = (double **)malloc(n *sizeof(double *));

            if (graph == NULL) {
                fprintf(stderr, "Cos sie zepsulo przy grafie\n");
                exit(EXIT_FAILURE);
            }

            for (int i = 0; i < n; i++) {
                graph[i] = (double *)malloc(n *sizeof(double));

                if (graph[i] == NULL) {
                    fprintf(stderr, "znowu przy grafie sie zepsulo graph[%d]\n", i);
                    exit(EXIT_FAILURE);
                }
            }

            make_graph(n, graph);
            // https://stackoverflow.com/questions/10192903/time-in-milliseconds-in-c
            struct timespec start, end;
            clock_gettime(CLOCK_MONOTONIC_RAW, &start);
            primMST(n, graph);
            clock_gettime(CLOCK_MONOTONIC_RAW, &end);
            uint64_t delta_us_prim = timespec_diff_us( &start, &end);

            clock_gettime(CLOCK_MONOTONIC_RAW, &start);
            kruskalMST(n, graph);
            clock_gettime(CLOCK_MONOTONIC_RAW, &end);
            uint64_t delta_us_kruskal = timespec_diff_us( &start, &end);

            #pragma omp critical
            {
                printf("%d %" PRIu64 " %" PRIu64 "\n", n, delta_us_prim, delta_us_kruskal);
                fflush(stdout);

                for (int i = 0; i < n; i++) {
                    free(graph[i]);
                }

                free(graph);
            }
        }
    }

    return 0;
}
