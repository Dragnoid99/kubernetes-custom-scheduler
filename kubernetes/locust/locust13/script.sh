#!/bin/bash

docker build -t locust-1-3 -f Dockerfile .

docker tag locust-1-3 dragnoid99/locust-1-3:latest

docker push dragnoid99/locust-1-3:latest
