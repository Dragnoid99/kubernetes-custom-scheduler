#!/bin/bash

cd qosscheduler/

python3 init.py

cd scheduler/code

while true;
do
	python3 scheduler.py
done
