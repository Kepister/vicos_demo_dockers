#! /bin/bash

ECHO="/tmp/echo.sock"

docker run -it \
--mount src=${ECHO},target=${ECHO},type=bind \
--entrypoint=/bin/bash echolibtest:3.5
