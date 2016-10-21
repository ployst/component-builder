# Used by builder to build and ship:
#
# `make build`
# `make test`
# `make release`
.PHONY: build test

build:
	echo "${VERSION}" > VERSION.txt
	pip install -r requirements/test.txt

test:
	bash adi/test.sh

release:
	bash adi/release.sh

version:
	echo "1.0.${BUILD_IDENTIFIER}"
