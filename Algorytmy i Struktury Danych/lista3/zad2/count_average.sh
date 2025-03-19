awk '{
    sumCH[$1] += $2
    sumSH[$1] += $3
    sumCQ[$1] += $4
    sumSQ[$1] += $5
    count[$1]++
}
END {
    for (key in sumCH) {
        print key, sumCH[key] / count[key], sumSH[key] / count[key], sumCQ[key] / count[key], sumSQ[key] / count[key], (sumCH[key] / count[key]) / key, (sumSH[key] / count[key]) / key, (sumCQ[key] / count[key]) / key , (sumSQ[key] / count[key]) /key
    }
}' random.txt | sort -n > average.txt
