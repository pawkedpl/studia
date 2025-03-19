#!/bin/bash
awk '{
    sumCT[$1] += $2
    sumST[$1] += $3
    sumTT[$1] += $4
    sumCF[$1] += $5
    sumSF[$1] += $6
    sumTF[$1] += $7
    sumCS[$1] += $8
    sumSS[$1] += $9
    sumTS[$1] += $10
    sumCN[$1] += $11
    sumSN[$1] += $12
    sumTN[$1] += $13
   count[$1]++
}
END {
    for (key in sumCT) {
        print key, sumCT[key] / count[key], sumST[key] / count[key], sumTT[key] / count[key],  sumCF[key] / count[key], sumSF[key] / count[key], sumTF[key] / count[key],  sumCS[key] / count[key], sumSS[key] / count[key], sumTS[key] / count[key],  sumCN[key] / count[key], sumSN[key] / count[key], sumTN[key] / count[key]  }
}' random.txt | sort -n > average.txt
