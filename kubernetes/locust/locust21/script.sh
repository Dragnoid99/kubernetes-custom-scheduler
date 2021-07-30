#!/bin/bash

docker build -t locust-2-1 -f Dockerfile .

docker tag locust-2-1 dragnoid99/locust-2-1:latest

docker push dragnoid99/locust-2-1:latest
