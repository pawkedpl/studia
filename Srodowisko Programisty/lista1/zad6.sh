#!/usr/bin/env bash

files=$(find "$1" -type f)

for file in $files
do
    awk ' {
        split($0, words, /[ ]/);
        delete count;
        for ( i in words ) {
            word = words[i];
            if ( word != "" ) count[word]++;
        }

        for ( word in count ) {
            if ( count[word] > 1 ) {
                print word, ":";
                print FILENAME, ":", NR, ":", $0;
            }
        }
    }' "${file}" | uniq
done
