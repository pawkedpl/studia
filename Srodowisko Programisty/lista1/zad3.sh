#!/usr/bin/env bash

words=$(find "$1" -type f -exec cat {} + | grep -o '\w*' | sort | uniq)
for word in $words
do
    count=$(grep -l -R -w "$word" "$1" | wc -l)
    echo "$count $word"
done | sort -r | uniq
