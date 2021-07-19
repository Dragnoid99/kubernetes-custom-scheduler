#!/bin/bash

docker build -t locust-0-1 -f Dockerfile .

docker tag locust-0-1 dragnoid99/locust-0-1:latest

docker push dragnoid99/locust-0-1:latest
