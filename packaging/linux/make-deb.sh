#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VERSION="${VERSION:?Set VERSION, for example 0.1.0}"
BUNDLE_DIR="${BUNDLE_DIR:-$ROOT/build/linux/dist/video-downloader-cua-zu}"
OUTPUT_DIR="${OUTPUT_DIR:-$ROOT/dist/release}"
PACKAGE_ROOT="$ROOT/build/linux/deb-root"

if [[ ! "$VERSION" =~ ^[0-9]+(\.[0-9]+)*([.+~][A-Za-z0-9.-]+)?$ ]]; then
    echo "Invalid Debian package version: $VERSION" >&2
    exit 1
fi
if [[ ! -x "$BUNDLE_DIR/video-downloader-cua-zu" ]]; then
    echo "Missing Linux application bundle: $BUNDLE_DIR/video-downloader-cua-zu" >&2
    exit 1
fi

rm -rf "$PACKAGE_ROOT"
install -d "$PACKAGE_ROOT/DEBIAN" "$PACKAGE_ROOT/opt/video-downloader-cua-zu" \
    "$PACKAGE_ROOT/usr/bin" "$PACKAGE_ROOT/usr/share/applications"
cp -a "$BUNDLE_DIR/." "$PACKAGE_ROOT/opt/video-downloader-cua-zu/"
install -m 0755 /dev/stdin "$PACKAGE_ROOT/usr/bin/video-downloader-cua-zu" <<'EOF'
#!/bin/sh
exec /opt/video-downloader-cua-zu/video-downloader-cua-zu "$@"
EOF
install -m 0644 "$ROOT/packaging/linux/video-downloader-cua-zu.desktop" \
    "$PACKAGE_ROOT/usr/share/applications/video-downloader-cua-zu.desktop"

cat > "$PACKAGE_ROOT/DEBIAN/control" <<EOF
Package: video-downloader-cua-zu
Version: $VERSION
Section: video
Priority: optional
Architecture: amd64
Depends: libc6 (>= 2.35), libpython3.10, libtcl8.6, libtk8.6, libssl3, libx11-6, libxext6, libxrender1, libxft2, libfontconfig1, zlib1g
Maintainer: Video Downloader Cua Zu contributors
Description: Desktop video downloader for supported websites
 Download videos from supported websites with a Vietnamese and English
 desktop interface.
EOF

mkdir -p "$OUTPUT_DIR"
dpkg-deb --root-owner-group --build "$PACKAGE_ROOT" \
    "$OUTPUT_DIR/video-downloader-cua-zu_${VERSION}_amd64.deb"
