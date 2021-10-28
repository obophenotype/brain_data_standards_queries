#!/usr/bin/env bash
set -e
docker build -t bds/search-service .
docker run -p 8484:8080 -it bds/search-service