#!/bin/bash

docker build -t locust-1-1 -f Dockerfile .

docker tag locust-1-1 dragnoid99/locust-1-1:latest

docker push dragnoid99/locust-1-1:latest
