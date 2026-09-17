#!/usr/bin/env bash
set -euo pipefail

python -m clipper_agent.cli doctor
python -m clipper_agent.cli clip "$@"
