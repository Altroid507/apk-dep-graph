#!/usr/bin/env bash
set -euo pipefail
PYTHONPATH="$(dirname "$0")/src" python3 -m src "$@"