#!/usr/bin/env bash
set -euo pipefail

usage() {
    printf 'Usage: %s [STREAMCONTROLLER_DATA_DIR]\n' "${0##*/}"
}

if [[ ${1:-} == --help || ${1:-} == -h ]]; then
    usage
    exit 0
fi
if (( $# > 1 )); then
    usage >&2
    exit 2
fi

source_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
data_dir=${1:-"$HOME/.var/app/com.core447.StreamController/data"}
plugins_dir="$data_dir/plugins"
destination="$plugins_dir/com_coffeesanvt_YAPS"

if [[ -d "$destination" && "$source_dir" -ef "$destination" ]]; then
    printf 'YAPS is already installed at %s\n' "$destination"
    exit 0
fi
if [[ -e "$destination" || -L "$destination" ]]; then
    printf 'YAPS already exists at %s. Move that folder before reinstalling.\n' "$destination" >&2
    exit 1
fi

mkdir -p -- "$plugins_dir"
temporary_dir=$(mktemp -d -- "$plugins_dir/.yaps-install.XXXXXXXX")
trap 'rm -rf -- "$temporary_dir"' EXIT
cp -R -- "$source_dir/"{main.py,actions.py,yaps.py,manifest.json,assets,LICENSE} "$temporary_dir/"
chmod 755 -- "$temporary_dir"
if ! mv -T -n -- "$temporary_dir" "$destination" || [[ -d "$temporary_dir" ]]; then
    printf 'Could not install YAPS at %s.\n' "$destination" >&2
    exit 1
fi
printf 'Installed YAPS at %s\nRestart StreamController to load the plugin.\n' "$destination"
