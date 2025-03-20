#!/usr/bin/env bash

find "$1" -type f -exec cat {} + | grep -o '\w*' | sort | uniq -c | sort -nr
