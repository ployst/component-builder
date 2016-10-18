#!/bin/bash
set -e
set -o pipefail

REPORT_LOCATION=${REPORT_LOCATION:-$PROJECT_DIR}

nosetests --with-xunit --xunit-file=$REPORT_LOCATION/nosetests.xml $PROJECT_DIR
flake8 operations/tools/builder/src | tee $REPORT_LOCATION/flake8.txt
