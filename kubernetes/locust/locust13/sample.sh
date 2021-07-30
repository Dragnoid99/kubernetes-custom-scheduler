#!/bin/bash
locust -f locustfile.py --host http://192.168.49.2:30001/service-1-3/polls/ --headless #-u 20 -r 20
