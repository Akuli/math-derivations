#!/bin/bash

source env/bin/activate

build()
{
    python3 build.py && linkchecker html/*.html html/*/*.html &
}

wait()
{
    inotifywait -e CLOSE_WRITE content/{*,*/*}.txt *.{py,css} js/*.js asymptote/*.asy
}

build
while wait; do build; done
