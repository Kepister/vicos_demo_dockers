#! /bin/bash

ECHO="/tmp/echo.sock"

docker run --rm -it \
--mount src=${ECHO},target=${ECHO},type=bind \
--entrypoint=python echolibtest:2.7 main.py
