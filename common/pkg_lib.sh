#!/bin/bash
set -e

# $1 - destdir, $2 - url
start_installation() {
    archive_name="$(basename "$2")"
    current_dir="$(realpath .)"

    if [ -f "$archive_name" ]; then
        echo "$archive_name already exists. Skipping build."
    else
        echo "Downloading archive $archive_name from $2..."
        wget "$2"

        echo "Extracting archive $archive_name..."
        dir_name=$(tar -tf "$archive_name" | head -1 | cut -f1 -d"/")
        tar -xf "$archive_name"
        dirnamerealpath="$(realpath "$dir_name")"
        cd "$dirnamerealpath"

        echo "Running configure step..."
        configure "$1"

        echo "Running build step..."
        build "$1"

        cd "$current_dir"
    fi

    echo "Running install step..."
    dir_name=$(tar -tf "$archive_name" | head -1 | cut -f1 -d"/")
    dirnamerealpath="$(realpath "$dir_name")"
    cd "$dirnamerealpath"

    install "$1"
    cd "$current_dir"
}
