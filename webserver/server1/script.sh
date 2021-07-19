#!/bin/bash

docker build -t app -f Dockerfile .

docker tag app dragnoid99/app:latest

docker push dragnoid99/app:latest
