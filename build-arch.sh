#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[build]'
python -m PyInstaller --clean --noconfirm --windowed --name video-downloader-cua-zu linktai.py
printf 'Da tao dist/video-downloader-cua-zu/video-downloader-cua-zu\n'
