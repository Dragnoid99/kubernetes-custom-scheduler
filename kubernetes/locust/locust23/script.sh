#!/bin/bash

docker build -t locust-2-3 -f Dockerfile .

docker tag locust-2-3 dragnoid99/locust-2-3:latest

docker push dragnoid99/locust-2-3:latest
