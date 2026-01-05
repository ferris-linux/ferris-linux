
# $1 - destdir, $2 - url
start_installation() {
    wget "$2"
    archive_name="$(basename $2)"
    dir_name=$(tar -tf "$archive_name" | head -1 | cut -f1 -d"/")
    tar -xf "$archive_name"
    current_dir="$(realpath .)"
    dirnamerealpath="$(realpath $dir_name)"
    cd "$dirnamerealpath"
    "configure" "$1"
    cd "$dirnamerealpath"
    "build" "$1"
    cd "$dirnamerealpath"
    "install" "$1"
    cd "$current_dir"
}
