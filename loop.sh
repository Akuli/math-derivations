#!/bin/bash

while true; do
    inotifywait -e CLOSE_WRITE content/*.txt content/*/*.txt *.py asymptote/*.asy
    python3 build.py
done
