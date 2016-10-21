#!/bin/bash
set -e
set -o pipefail

export REPORT_LOCATION=${REPORT_LOCATION:-.}

tox

flake8 src | tee $REPORT_LOCATION/flake8.txt
