#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VERSION="${VERSION:?Set VERSION, for example 0.1.0}"
BUNDLE_DIR="${BUNDLE_DIR:-$ROOT/build/linux/dist/video-downloader-cua-zu}"
OUTPUT_DIR="${OUTPUT_DIR:-$ROOT/dist/release}"
RPM_TOP="$ROOT/build/linux/rpmbuild"

if [[ ! "$VERSION" =~ ^[0-9]+(\.[0-9]+)*([.+~][A-Za-z0-9.-]+)?$ ]]; then
    echo "Invalid RPM package version: $VERSION" >&2
    exit 1
fi
if [[ ! -x "$BUNDLE_DIR/video-downloader-cua-zu" ]]; then
    echo "Missing Linux application bundle: $BUNDLE_DIR/video-downloader-cua-zu" >&2
    exit 1
fi

rm -rf "$RPM_TOP"
mkdir -p "$RPM_TOP/BUILD" "$RPM_TOP/BUILDROOT" "$RPM_TOP/RPMS" \
    "$RPM_TOP/SOURCES" "$RPM_TOP/SPECS" "$RPM_TOP/SRPMS" "$OUTPUT_DIR"
tar -czf "$RPM_TOP/SOURCES/video-downloader-cua-zu-bundle.tar.gz" \
    -C "$(dirname "$BUNDLE_DIR")" "$(basename "$BUNDLE_DIR")"
cp "$ROOT/packaging/linux/video-downloader-cua-zu.desktop" "$RPM_TOP/SOURCES/"
cp "$ROOT/LICENSE" "$RPM_TOP/SOURCES/"
cp "$ROOT/packaging/linux/video-downloader-cua-zu.spec" "$RPM_TOP/SPECS/"

rpmbuild -bb "$RPM_TOP/SPECS/video-downloader-cua-zu.spec" \
    --define "_topdir $RPM_TOP" \
    --define "app_version $VERSION"
find "$RPM_TOP/RPMS" -type f -name '*.rpm' -exec cp {} "$OUTPUT_DIR/" \;
