#!/bin/bash

docker build -t locust-1-2 -f Dockerfile .

docker tag locust-1-2 dragnoid99/locust-1-2:latest

docker push dragnoid99/locust-1-2:latest
