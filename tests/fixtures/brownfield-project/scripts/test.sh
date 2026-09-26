#!/usr/bin/env bash
set -euo pipefail
python3 -m unittest discover -s qa -p 'test_*.py'
