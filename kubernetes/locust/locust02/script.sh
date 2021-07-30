#!/bin/bash

docker build -t locust-0-2 -f Dockerfile .

docker tag locust-0-2 dragnoid99/locust-0-2:latest

docker push dragnoid99/locust-0-2:latest
