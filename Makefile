# Used by builder to build and ship:
#
# `make build`
# `make test`
# `make release`

export PROJECT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
export ADI_DIR:=${PROJECT_DIR}/adi
export ROOT_DIR:=$(shell dirname "${PROJECT_DIR}")

.PHONY: build test

build:
	echo "${VERSION}" > VERSION.txt
	pip install -r ${PROJECT_DIR}/requirements/test.txt

test:
	bash ${ADI_DIR}/test.sh

release:
	bash ${ADI_DIR}/release.sh

version:
	echo "1.0.${BUILD_IDENTIFIER}"
