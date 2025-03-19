awk '{
    sumCH[$1] += $2
    sumSH[$1] += $3
    count[$1]++
}
END {
    for (key in sumCH) {
        print key, sumCH[key] / count[key], sumSH[key] / count[key]    }
}' results.txt | sort -n > average.txt
