#!/bin/bash
# Sync asymptote-built images from what is currently published to gh-pages.
# This prevents having to rebuild everything.

set -ex

dir="$(mktemp -d)"
trap 'rm -rf "$dir"' exit

mkdir -p imagecache
repo="$PWD"
cd "$dir"

git clone --depth=1 --branch=gh-pages https://github.com/Akuli/math-derivations
cd math-derivations
git checkout gh-pages
mv asymptote/* "$repo"/imagecache
