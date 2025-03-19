set title "Average COMPARISONS for finding the element RANDOM"
set style data lines
set xlabel "n"
set ylabel "Average comp"
set title font "Helvetica,14"

plot "average.txt" using 1:2 t "BinarySearch"

