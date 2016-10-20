#!/bin/bash

PYPIRC=~/.pypirc
cp $PYPIRC /tmp/pypirc

read -d '' content << EOF
[distutils]
index-servers=
    pypi
    test

[pypi]
repository = https://pypi.python.org/pypi
username = $PYPI_USERNAME
password = $PYPI_PASSWORD
EOF

echo "$content" > $PYPIRC

cat $PYPIRC

python setup.py sdist bdist_wheel upload -r pypi

cp /tmp/pypirc $PYPIRC
