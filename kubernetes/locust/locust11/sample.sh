#!/bin/bash
locust -f locustfile.py --host http://10.101.100.199/service-1-1/polls/ --headless #-u 20 -r 20
