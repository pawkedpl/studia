set title "Average SWAPS for finding FIRST statistics"
set style data lines
set xlabel "n"
set ylabel "Average swaps"

plot "average.txt" using 1:3 t "SelectRandom", \
"" using 1:5 t "SelectFive"
