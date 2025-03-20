#!/usr/bin/env bash

words=$(find "$1" -type f -exec cat {} + | grep -o '\w*' | sort | uniq)

for word in $words
do
    echo ""
    echo "$word:"
    grep -r -n -w "$word" "$1"
done 
