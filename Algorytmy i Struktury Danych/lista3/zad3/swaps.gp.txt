set title "Average SWAPS for finding MIDDLE statistics"
set style data lines
set xlabel "n"
set ylabel "Average swaps"

plot "average.txt" using 1:3 t "SelectThree", \
"" using 1:6 t "SelectFive", \
"" using 1:9 t "SelectSeven", \
"" using 1:12 t "SelectNine"
