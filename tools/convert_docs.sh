#!/bin/bash

CHANGELOG=docs/changelog.rst

filename="${CHANGELOG%.*}"
echo "Converting $CHANGELOG to $filename.md"
pandoc --wrap=preserve $CHANGELOG -f rst -t markdown -o "$filename".md
