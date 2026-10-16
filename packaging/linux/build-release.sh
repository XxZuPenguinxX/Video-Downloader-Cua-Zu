#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FORMAT="${1:?Usage: build-release.sh deb|rpm}"
VERSION="${VERSION:?Set VERSION, for example 0.1.0}"
BUILD_ROOT="$ROOT/build/linux"
VENV="$BUILD_ROOT/venv"

mkdir -p "$BUILD_ROOT" "$ROOT/dist/release"
python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install -e "$ROOT[build]"
"$VENV/bin/python" -m PyInstaller \
    --clean \
    --noconfirm \
    --windowed \
    --name video-downloader-cua-zu \
    --distpath "$BUILD_ROOT/dist" \
    --workpath "$BUILD_ROOT/work" \
    --specpath "$BUILD_ROOT/spec" \
    "$ROOT/linktai.py"

case "$FORMAT" in
    deb)
        BUNDLE_DIR="$BUILD_ROOT/dist/video-downloader-cua-zu" \
            VERSION="$VERSION" bash "$ROOT/packaging/linux/make-deb.sh"
        ;;
    rpm)
        BUNDLE_DIR="$BUILD_ROOT/dist/video-downloader-cua-zu" \
            VERSION="$VERSION" bash "$ROOT/packaging/linux/make-rpm.sh"
        ;;
    *)
        echo "Unsupported package format: $FORMAT" >&2
        exit 1
        ;;
esac
