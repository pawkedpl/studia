set title "Average COMPARISONS for finding FIRST statistics"
set style data lines
set xlabel "n"
set ylabel "Average comparisons"
set title font "Helvetica,14"

plot "average.txt" using 1:2 t "SelectRandom", \
"" using 1:4 t "SelectFive"

