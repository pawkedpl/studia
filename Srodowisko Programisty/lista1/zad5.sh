#!/usr/bin/env bash

files=$(find "$1" -type f)

for file in $files
do
    sed -i "s/a/A/g" "$file"
done
