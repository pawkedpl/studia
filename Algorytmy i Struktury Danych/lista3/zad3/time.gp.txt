set title "Average TIME for finding MIDDLE statistics"
set style data lines
set xlabel "n"
set ylabel "Average time"

plot "average.txt" using 1:4 t "SelectThree", \
"" using 1:7 t "SelectFive", \
"" using 1:10 t "SelectSeven", \
"" using 1:13 t "SelectNine"
