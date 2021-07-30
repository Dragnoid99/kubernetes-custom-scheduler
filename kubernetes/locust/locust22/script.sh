#!/bin/bash

docker build -t locust-2-2 -f Dockerfile .

docker tag locust-2-2 dragnoid99/locust-2-2:latest

docker push dragnoid99/locust-2-2:latest
