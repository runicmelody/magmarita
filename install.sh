#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -z "$PYTHON" ]; then PYTHON=python3; fi
exec "$PYTHON" "$DIR/install.py" "$@"
