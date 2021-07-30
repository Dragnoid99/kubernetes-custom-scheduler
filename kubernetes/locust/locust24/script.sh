#!/bin/bash

docker build -t locust-2-4 -f Dockerfile .

docker tag locust-2-4 dragnoid99/locust-2-4:latest

docker push dragnoid99/locust-2-4:latest
