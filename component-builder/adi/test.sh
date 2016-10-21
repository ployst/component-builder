#!/bin/bash
set -e
set -o pipefail

REPORT_LOCATION=${REPORT_LOCATION:-.}

nosetests --with-xunit --xunit-file=$REPORT_LOCATION/nosetests.xml -s .

flake8 src | tee $REPORT_LOCATION/flake8.txt
