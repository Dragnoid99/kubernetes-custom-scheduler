#!/bin/bash

docker build -t locust-2-5 -f Dockerfile .

docker tag locust-2-5 dragnoid99/locust-2-5:latest

docker push dragnoid99/locust-2-5:latest
