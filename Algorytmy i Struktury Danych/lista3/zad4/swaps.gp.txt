set title "Average TIME for finding element RANDOM"
set style data lines
set xlabel "n"
set ylabel "Average time"

plot "average.txt" using 1:3 t "BinarySearch"
