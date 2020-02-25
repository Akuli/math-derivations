#!/bin/bash

build()
{
    python3 build.py
}

wait()
{
    inotifywait -e CLOSE_WRITE content/{*,*/*}.txt *.{py,css} asymptote/*.asy
}

build
while wait; do build; done
