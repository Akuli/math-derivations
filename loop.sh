#!/bin/bash

build()
{
    python3 build.py
}

wait()
{
    inotifywait -e CLOSE_WRITE content/*.txt content/*/*.txt *.py asymptote/*.asy
}

build
while wait; do build; done
