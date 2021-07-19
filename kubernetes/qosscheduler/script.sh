#!/bin/bash

docker build -t qos-scheduler -f Dockerfile .

docker tag qos-scheduler dragnoid99/qos-scheduler:latest

docker push dragnoid99/qos-scheduler:latest
