all: astyle tests

tests: tests.c
	gcc -Wpedantic -Wall -Wextra -fopenmp -o tests tests.c -ldl

clean:
	rm tests *.orig 

astyle:
	astyle --style=attach --break-blocks --pad-oper --pad-header --align-pointer=name --align-reference=name generate_graph.h prim.h kruskal.h tests.c

