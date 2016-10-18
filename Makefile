# Used by builder to build and ship:
#
# `make build`
# `make test`
# `make release`

export PROJECT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
export ADI_DIR:=${PROJECT_DIR}/adi
export ROOT_DIR:=$(shell dirname "${PROJECT_DIR}")

build:
	bash ${ADI_DIR}/build.sh

test:
	bash ${ADI_DIR}/test.sh
