FROM alpine:latest

RUN apk --update add bash curl ca-certificates git build-base \
    libffi-dev openssl-dev libbz2 libc6-compat ncurses-dev readline-dev \
    xz-dev zlib-dev sqlite-dev patch bzip2-dev expat-dev zlib-dev \
    gdbm-dev paxmark linux-headers tcl-dev jpeg-dev

COPY setup.sh /setup.sh

RUN /bin/bash /setup.sh \
    && rm /setup.sh

ENV HOME /root
ENV PYENV_ROOT $HOME/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH
